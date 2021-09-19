from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from multiselectfield import MultiSelectField

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






class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    ordering = models.IntegerField(default=0)

    class Meta:
        ordering = ['ordering']
    
    def __str__(self):
        return self.title



class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=15)
    image = models.ImageField(upload_to = "uploads/", null = True, blank = True)
    price = models.FloatField()
    date_added = models.DateTimeField(auto_now_add=True)

    #class Meta:
        #ordering = ['-price']      # default ordering whenever you query to database    retrieval in order as stored in DB ---> ordering ---> returned as a queryset where called

    @classmethod
    def updateprice(cls,product_id, price):
        product = cls.objects.filter(product_id = product_id)
        product = product.first()
        product.price = price
        product.save()
        return product

    @classmethod
    def create(cls, product_name, price):
        product = Product(product_name = product_name, price = price)
        product.save()
        return product
    

    # @staticmethod
    # def a_static_method():
    #     """A static method has no information about instances or classes
    #     unless explicitly given. It just lives in the class (and thus its 
    #     instances') namespace.
    #     """
    #     return some_function_h()

    def __str__(self):
        return self.product_name




class CartManager(models.Manager):
    def create_cart(self, user):
        cart = self.create(user = user)
        # you can perform more operations 
        return cart

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    created_on = models.DateTimeField(default=timezone.now)

    objects = CartManager()

class ProductInCart(models.Model):
    class Meta:
        unique_together = (('cart', 'product'),)
    product_in_cart_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField()