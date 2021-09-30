from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy
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


    
    # change password
    path('profile/password_change/', auth_views.PasswordChangeView.as_view(template_name='core/registration/password_change.html', success_url = reverse_lazy("password_change_done")), 
        name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='core/registration/password_change_done.html'), 
        name='password_change_done'),



    #Forgot password
    
    path('login/reset_password/',auth_views.PasswordResetView.as_view(template_name = "core/registration/password_reset.html", success_url = reverse_lazy("password_reset_done"), email_template_name = 'core/registration/forgot_password_email.html'), 
    name="reset_password"),     # 1
    path('reset_password_sent/',auth_views.PasswordResetDoneView.as_view(template_name = "core/registration/password_reset_sent.html"), 
    name="password_reset_done"),    # 2
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name = "core/registration/password_reset_form.html", success_url = reverse_lazy("password_reset_complete")), 
    name="password_reset_confirm"),  # 3
    path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name = "core/registration/password_reset_done.html"), 
    name="password_reset_complete"),   # 4







   


    path('profile/',views.profile.as_view(),name='profile'),


    
  
    path('products/', views.all_products, name='products'),
    path('men/',views.mens_products, name='mens_products'),
    path('women/', views.womens_products, name='womens_products'),
    path('product_showcase/<id>',views.product_showcase,name='product_showcase'),

    path('search/',views.do_search,name='search'),
   
   path('view_cart/',views.view_cart, name="view_cart"),
   path('add/<id>',views.add_to_cart,name="add_to_cart"),
   path('adjust/<id>',views.adjust_cart,name="adjust_cart"),
   path('remove_cart/<id>',views.remove_cart,name="remove_cart"),


   path('checkout/',views.checkout,name="checkout"),
  


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
