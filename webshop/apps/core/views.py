
from django.http import request
from django.shortcuts import render,  HttpResponse, redirect,get_object_or_404
from django.views.generic import CreateView,FormView
from .forms import  CustomUserChangeForm, RegistrationFormCustomer,BillingAddressForm,ContactUsForm,OrderForm,MakePaymentForm
from .models import  CustomUser,BillingAddress
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from django.db.models import Q
from webshop import settings
from django.conf import settings
from django.core.mail import send_mail
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Product,GenderFilter,Order,OrderLineItem
from django.http import HttpResponseRedirect
import stripe


#from apps.product.models import Product

# Create your views here.
def frontpage(request):
    newest_products = Product.objects.all()[0:8]

    return render(request, 'core/frontpage.html', {'newest_products': newest_products})





class RegisterView(CreateView):
    template_name = 'core/registerbasicuser.html'
    form_class = RegistrationFormCustomer
    success_url = reverse_lazy('signup')

    def post(self, request, *args, **kwargs):
        #form = RegistrationForm(request.POST)
        user_email = request.POST.get('email')
        try:
            existing_user = CustomUser.objects.get(email = user_email)
            if(existing_user.is_active == False):
                existing_user.delete()
        except:
            pass
        response = super().post(request, *args, **kwargs)
        if response.status_code == 302:
            user = CustomUser.objects.get(email = user_email)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)      #127.0.0.1:8000 
            mail_subject = 'Activate your account.'
            message = render_to_string('core/registration/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            #print(message)
            to_email = user_email   
            #form = RegistrationForm(request.POST)   # here we are again calling all its validations
            form = self.get_form()
            try:
                send_mail(
                    subject=mail_subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list= [to_email],
                    fail_silently=False,    # if it fails due to some error or email id then it get silenced without affecting others
                )
                messages.success(request, "link has been sent to your email id. please check your inbox and if its not there check your spam as well.")
                return self.render_to_response({'form':form})
            except:
                form.add_error('', 'Error Occured In Sending Mail, Try Again')
                messages.error(request, "Error Occured In Sending Mail, Try Again")
                return self.render_to_response({'form':form})
        else:
            return response

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist) as e:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Successfully Logged In")
        return redirect(reverse_lazy('frontpage'))
        # return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid or your account is already Verified! Try To Login')


class LoginViewUser(LoginView):
    template_name = "core/login.html"
    

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect('frontpage')



def contactus(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():      #clean_data
            if len(form.cleaned_data.get('query'))>10:
                form.add_error('query', 'Query length is not right')
                return render(request, 'core/contact.html', {'form':form})
            form.save()
            return HttpResponse("Thank YOu")
        else:
            if len(form.cleaned_data.get('query'))>10:
                #form.add_error('query', 'Query length is not right')
                form.errors['__all__'] = 'Query length is not right. It should be in 10 digits.'
            return render(request, 'core/contact.html', {'form':form})
    return render(request, 'core/contact.html', {'form':ContactUsForm})


class profile(FormView):
    form_class=CustomUserChangeForm
    template_name='core/profile.html'
    success_url=reverse_lazy('profile')




# @login_required
# def profile(request):
#     """
#     Shows the customer their current billing address details.
#     Allows the customer to update their billing address details.
#     Creates a new billing address on completion.
#     """

#     billing_address = BillingAddress.objects.filter(user=request.user).first()
#     if request.method == "POST":
#         billing_form = BillingAddressForm(request.POST, instance=billing_address)
#         if billing_form.is_valid():
#             billing_address = billing_form.save(commit=False)
#             billing_address.user = request.user
#             billing_address.save()
#             messages.success(request,
#                              "Your billing address has been updated successfully")
#     else:
#         billing_form = BillingAddressForm(instance=billing_address)

#     return render(request, 'core/profile.html', {"billing_form": billing_form})


def all_products(request):
    products = Product.objects.all()
    return render(request, 'core/parts/products.html', {'products': products})


def mens_products(request):
    person_category = GenderFilter.objects.filter(category="M")
    products = Product.objects.filter(person_category=person_category[0])
    return render(request, 'core/parts/products.html', {'products': products})


def womens_products(request):
    person_category = GenderFilter.objects.filter(category="W")
    products = Product.objects.filter(person_category=person_category[0])
    return render(request, 'core/parts/products.html', {"products": products})


def product_showcase(request, id):
    
    product =Product.objects.get(id=id)
   
    
    return render(request, 'core/parts/product_showcase.html', {"product": product})



def view_cart(request):
    """A View that renders the cart contents page"""
    return render(request, "core/parts/cart.html")


def do_search(request):
    products = Product.objects.filter(title__icontains=request.GET['query'])
    if products:
        return render(request, "core/parts/products.html", {"products": products})
    else:
        return render(request, "core/frontpage.html")




def add_to_cart(request, id):
    """Add a quantity of the specified product to the cart"""

    quantity = int(request.POST.get('quantity'))
    cart = request.session.get('apps', {})
    if id in cart:
        cart[id] = int(cart[id]) + quantity
    else:
        cart[id] = cart.get(id, quantity)

    request.session['apps'] = cart
    return_path = request.POST.get('return_path','/')
    return HttpResponseRedirect(return_path)


def adjust_cart(request, id):
    """
    Adjust the quantity of the specified product to the specified
    amount
    """
    print(request.POST)
    
    quantity = int(request.POST.get('quantity'))
    cart = request.session.get('apps', {})

    if quantity > 0:
        cart[id] = quantity
    else:
        cart.pop(id)


    request.session['apps'] = cart
    return redirect(reverse('view_cart'))


def remove_cart(request, id):
    cart = request.session.get('apps', {})
    if cart:
        cart.pop(id)

    request.session['apps'] = cart
    return redirect(reverse('view_cart'))






stripe.api_key = settings.STRIPE_SECRET


@login_required()
def checkout(request):
    if request.method == "POST":
        order_form = OrderForm(request.POST)
        payment_form = MakePaymentForm(request.POST)

        if order_form.is_valid() and payment_form.is_valid():
            order = order_form.save(commit=False)
            order.date = timezone.now()
            order.save()

            cart = request.session.get('apps', {})
            total = 0
            for id, quantity in cart.items():
                product = get_object_or_404(Product, pk=id)
                total += quantity * product.price
                order_line_item = OrderLineItem(
                    order=order,
                    product=product,
                    quantity=quantity
                )
                order_line_item.save()

            try:
                customer = stripe.Charge.create(
                    amount=int(total * 100),
                    currency="EUR",
                    description=request.user.email,
                    card=payment_form.cleaned_data['stripe_id'],
                )
            except stripe.error.CardError:
                messages.error(request, "Your card was declined!")

            if customer.paid:
                messages.error(request, "You have successfully paid")
                request.session['apps'] = {}
                return redirect(reverse('frontpage'))
            else:
                messages.error(request, "Unable to take payment")
        else:
            print(payment_form.errors)
            messages.error(request,
                           "We were unable to take a payment with that card!"
                           )
    else:
        payment_form = MakePaymentForm()
        order_form = OrderForm()

    return render(request, "core/checkout.html", {
        'order_form': order_form,
        'payment_form': payment_form,
        'publishable': settings.STRIPE_PUBLISHABLE
        }
    )





