from django.contrib import admin

from apps.radiodns_auth.models import User


class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Authentication Data", {"fields": ["username", "password"]}),
        ("Personal Data", {"fields": ["first_name", "last_name", "email"]}),
        ("Access", {"fields": ["is_staff", "is_active"]}),
    ]
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "is_active",
    )


admin.site.register(User, UserAdmin)
