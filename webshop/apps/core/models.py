from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User
from .choices import BRAND_CHOICES, PRODUCT_CATEGORY_CHOICES, SIZE_CHOICES

from .managers import CustomUserManager


# Create your models here.
class LowercaseEmailField(models.EmailField):
    """
    Override EmailField to convert emails to lowercase before saving.
    """
    def to_python(self, value):
        """
        Convert email to lowercase.
        """
        value = super(LowercaseEmailField, self).to_python(value)
        # Value can be None so check that it's a string before lowercasing.
        if isinstance(value, str):
            return value.lower()
        return value




class CustomUser(AbstractBaseUser, PermissionsMixin):
    # username = None
    email = LowercaseEmailField(_('email address'), unique=True)
    name = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    # if you require phone number field in your project
    phone_regex = RegexValidator( regex = r'^\d{10}$',message = "phone number should exactly be in 10 digits")
    phone = models.CharField(max_length=255, validators=[phone_regex], blank = True, null=True)  # you can set it unique = True


    class Types(models.TextChoices):
        SELLER = "Seller", "SELLER"
        CUSTOMER = "Customer", "CUSTOMER"

    

    default_type = Types.CUSTOMER


    type = MultiSelectField(choices=Types.choices, default=[], null=True, blank=True)


    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    #place here
        # if not the code below then taking default value in User model not in proxy models
    def save(self, *args, **kwargs):
        if not self.id:
            #self.type = self.default_type
            self.type.append(self.default_type)
        return super().save(*args, **kwargs)






class SellerAdditional(models.Model):
    user = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    gst = models.CharField(max_length=10)
    warehouse_location = models.CharField(max_length=1000)


class SellerManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        #return super().get_queryset(*args, **kwargs).filter(type = CustomUser.Types.SELLER)
        return super().get_queryset(*args, **kwargs).filter(Q(type__contains = CustomUser.Types.SELLER))



class Seller(CustomUser):
    default_type = CustomUser.Types.SELLER
    objects = SellerManager()
    class Meta:
        proxy = True
    
    def sell(self):
        print("I can sell")

    @property
    def showAdditional(self):
        return self.selleradditional



class CustomerAdditional(models.Model):
    user = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    address = models.CharField(max_length=1000)



class CustomerManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        #return super().get_queryset(*args, **kwargs).filter(type = CustomUser.Types.CUSTOMER)
        return super().get_queryset(*args, **kwargs).filter(Q(type__contains = CustomUser.Types.CUSTOMER))


class Customer(CustomUser):
    default_type = CustomUser.Types.CUSTOMER
    objects = CustomerManager()
    class Meta:
        proxy = True 

    def buy(self):
        print("I can buy")

    @property
    def showAdditional(self):
        return self.customeradditional



class Contact(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=5)
    phone_regex = RegexValidator( regex = r'^\d{10}$',message = "phone number should exactly be in 10 digits")
    phone = models.CharField(max_length=255, validators=[phone_regex])
    query = models.TextField()




class BillingAddress(models.Model):
    user = models.OneToOneField(Customer, on_delete = models.CASCADE)
    full_name = models.CharField(max_length=42)
    street_address_1 = models.CharField(max_length=32)
    street_address_2 = models.CharField(max_length=32)
    city = models.CharField(max_length=24)
    postcode = models.CharField(max_length=12)
    county = models.CharField(max_length=24)
    country = models.CharField(max_length=32)
    phone_number = models.CharField(max_length=16)




    def __str__(self):
        return self.user.name



class GenderFilter(models.Model):  
    category = models.CharField(max_length=1)

    def __str__(self):
        return self.category




class Product(models.Model):
    person_category = models.ForeignKey(GenderFilter,
                                        blank=True,
                                        null=True,
                                        on_delete=models.SET_NULL)

    brand = models.CharField(max_length=6,
                             choices=BRAND_CHOICES,
                             default='LABONE')

    product_category = models.CharField(max_length=6,
                                        choices=PRODUCT_CATEGORY_CHOICES,
                                        default='JACPAR')

    title = models.CharField(max_length=100,
                             default='',
                             blank=False)

    description = models.TextField(blank=False)

    size = models.CharField(max_length=3,
                            choices=SIZE_CHOICES,
                            default='NA')

    price = models.DecimalField(max_digits=10,
                                decimal_places=3,
                                blank=False)
    

    image = models.ImageField(upload_to='uploads/',default = None, null = True, blank = True)

    quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.title

class Order(models.Model):
    full_name = models.CharField(max_length=50, blank=False)
    street_address_1 = models.CharField(max_length=40, blank=False)
    city = models.CharField(max_length=40, blank=False)
    postcode = models.CharField(max_length=20, blank=True)
    county = models.CharField(max_length=40, blank=False)
    country = models.CharField(max_length=40, blank=False)
    phone_number = models.CharField(max_length=20, blank=False)
    date = models.DateField()

    def __str__(self):
        return "{0}-{1}-{2}".format(
            self.id,
            self.date,
            self.full_name)


class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, null=False,on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=False,on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=False)

    def __str__(self):
        return "{0} {1} @ {2}".format(
            self.quantity,
            self.product.title,
            self.product.price)






