from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser,Seller, SellerAdditional,Customer,Product
from django.forms import ModelForm
from django.core.validators import RegexValidator
from django import forms


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email',)




class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email',)




class RegistrationForm(UserCreationForm):
    class Meta:
        model = Seller
        fields = [
            'email',
            'name',
            'password1',
            'password2',
        ]

class RegistrationFormSeller(UserCreationForm):
    gst = forms.CharField(max_length=10)
    warehouse_location = forms.CharField(max_length=1000)
    class Meta:
        model = Seller
        fields = [
            'email',
            'name',
            'password1',
            'password2',
            'gst',
            'warehouse_location'
        ]

class RegistrationFormSeller2(forms.ModelForm):
    class Meta:
        model = SellerAdditional
        fields = [
            'gst',
            'warehouse_location'
        ]


class SendOtpBasicForm(forms.Form):
    phone_regex = RegexValidator( regex = r'^\d{10}$',message = "phone number should exactly be in 10 digits")
    phone = forms.CharField(max_length=255, validators=[phone_regex])

    class Meta:
        fields = [
            'phone',
        ]

class VerifyOtpBasicForm(forms.Form):
    otp_regex = RegexValidator( regex = r'^\d{4}$',message = "otp should be in six digits")
    otp = forms.CharField(max_length=6, validators=[otp_regex])

    # class Meta:
    #     field



class RegistrationFormCustomer(UserCreationForm):
    class Meta:
        model = Customer
        fields = [
            'email',
            'name',
            'password1',
            'password2',
        ]




class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'image', 'product_name', 'price']


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField()