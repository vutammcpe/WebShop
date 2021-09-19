from django.http import request
from django.shortcuts import render,  HttpResponse, redirect,get_object_or_404
from django.views.generic import CreateView,DetailView, ListView, UpdateView, DeleteView
from .forms import RegistrationForm, RegistrationFormCustomer, ProductForm,CartForm
from .models import Customer, CustomUser,Cart,ProductInCart
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


import random
from webshop import settings
from django.core.mail import send_mail
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Product


#from apps.product.models import Product

# Create your views here.
def frontpage(request):
    newest_products = Product.objects.all()[0:8]

    return render(request, 'core/frontpage.html', {'newest_products': newest_products})

def contact(request):
    return render(request, 'core/contact.html')



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
            current_site = get_current_site(request)     #www.wondershop.in:8000  127.0.0.1:8000 
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

@login_required
def admin_custom(request):
    view = Product.objects.all()
    return render(request, 'core/admin_cus.html',{'view': view})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)
            product.save()

            return redirect('admin_custom')
    else:
        form = ProductForm()
    
    return render(request, 'core/parts/add_product.html', {'form': form})


class ProductDetail(DetailView):
    model = Product
    template_name = "core/parts/product_details.html"
    context_object_name = "product"



@login_required
def addToCart(request, id):
    try:
        cart = Cart.objects.get(user = request.user)
        try:
            product = Product.objects.get(product_id = id)
            try:
                productincart = ProductInCart.objects.get(cart = cart, product = product)
                productincart.quantity = productincart.quantity + 1
                productincart.save()
                messages.success(request, "Successfully added to cart")
                return redirect(reverse_lazy("displaycart"))
            except:
                productincart = ProductInCart.objects.create(cart = cart, product = product, quantity=1)
                messages.success(request, "Successfully added to cart")
                return redirect(reverse_lazy("displaycart"))
        except:
            messages.error(request, "Product can not be found")
            return redirect(reverse_lazy('frontpage'))
    except:
        cart = Cart.objects.create(user = request.user)
        try:
            product = Product.objects.get(product_id = id)
            productincart = ProductInCart.objects.create(cart = cart, product = product, quantity = 1)
            messages.success(request, "Successfully added to cart")
            return redirect(reverse_lazy("displaycart"))
        except:
            messages.error(request, "Error in adding to cart. Please try again")
            return redirect(reverse_lazy('frontpage'))


class DisplayCart(LoginRequiredMixin, ListView):
    model = ProductInCart
    template_name = "core/parts/display_cart.html"
    context_object_name = "cart"

    def get_queryset(self):
        queryset = ProductInCart.objects.filter(cart = self.request.user.cart)
        return queryset
        



class UpdateCart(LoginRequiredMixin, UpdateView):
    model = ProductInCart
    form_class = CartForm
    success_url = reverse_lazy("displaycart")

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 302:
            if int(request.POST.get("quantity")) == 0:
                productincart = self.get_object()
                productincart.delete()
            return response
        else:
            messages.error(request, "error in quantity")
            return redirect(reverse_lazy("displaycart"))

class DeleteFromCart(LoginRequiredMixin, DeleteView):
    model = ProductInCart
    success_url = reverse_lazy("displaycart")  