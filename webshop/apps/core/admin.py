from django.contrib import admin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin
from .models import   CustomUser, Customer,SellerAdditional,Seller,Product,GenderFilter,Contact
# Register your models here.


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'phone', 'name','type', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions',)}),   #'is_customer' , 'is_seller'
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'name', 'type', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)




class SellerAdditionalInline(admin.TabularInline):
    model = SellerAdditional


class SellerAdmin(admin.ModelAdmin):
    inlines = (
        SellerAdditionalInline,
    )





admin.site.register(Contact)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Customer)
admin.site.register(Seller, SellerAdmin)
admin.site.register(SellerAdditional)


admin.site.register(GenderFilter)
admin.site.register(Product)