from django.urls import path
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from . import views
from webshop import settings
from django.contrib.staticfiles.urls import static


urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', views.frontpage , name='frontpage'),
    path('contact/', views.contactus , name='contact'),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicons/favicon-16x16.png'))),


    path('signup/', views.RegisterView.as_view(), name="signup"),
    path('login/', views.LoginViewUser.as_view(), name="login"),
    path('logout/', views.logout_request, name="logout"),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),

   


    path('profile/',views.BillingAddress,name='profile'),


    
  
    path('products/', views.all_products, name='products'),
    path('men/',views.mens_products, name='mens_products'),
    path('women/', views.womens_products, name='womens_products'),
    path('product_showcase/<id>',views.product_showcase,name='product_showcase'),


   
   path('view_cart/',views.view_cart, name="view_cart"),
   path('add/<id>',views.add_to_cart,name="add_to_cart"),
   path('adjust/<id>',views.adjust_cart,name="adjust_cart"),
   path('remove_cart/<id>',views.remove_cart,name="remove_cart"),
  


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
