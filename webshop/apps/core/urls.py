from django.urls import path
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from . import views
from webshop import settings
from django.contrib.staticfiles.urls import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.frontpage , name='frontpage'),
    path('contact/', views.contact , name='contact'),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicons/favicon-16x16.png'))),


    path('signup/', views.RegisterView.as_view(), name="signup"),
    path('login/', views.LoginViewUser.as_view(), name="login"),
    path('logout/', views.logout_request, name="logout"),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('admin_custom/',views.admin_custom,name='admin_custom'),
    path('add_product/',views.add_product,name='add_product'),
    path('productdetail/<int:pk>/', views.ProductDetail.as_view(), name="productdetail"),
    path('addtocart/<int:id>/', views.addToCart, name="addtocart"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
