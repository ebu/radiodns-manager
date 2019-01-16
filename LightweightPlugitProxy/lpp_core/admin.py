from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from lpp_core.forms import CustomUserCreationForm, CustomUserChangeForm
from lpp_core.models import Organization, LppUser


class CustomLppUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = LppUser
    list_display = ['username', 'email', "organization", ]
    fieldsets = (
        (None, {'fields': ('username', 'password', 'organization')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
    )


admin.site.register(Organization)
admin.site.register(LppUser, CustomLppUserAdmin)
