from django.contrib import admin
from django.contrib.auth.models import Group
from apps.radiodns_auth.models import User
from social_django.models import Association, Nonce, UserSocialAuth
from apps.manager.admin import OrganizationAdminInline


class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Authentication Data", {"fields": ["username", "password"]}),
        ("Personal Data", {"fields": ["first_name", "last_name", "email"]}),
        ("Access", {"fields": ["is_superuser", "is_staff", "is_active"]}),
    ]
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "is_superuser",
        "is_active",
    )
    inlines = (OrganizationAdminInline, )


admin.site.unregister(Group)
admin.site.unregister(Association)
admin.site.unregister(Nonce)
admin.site.unregister(UserSocialAuth)
admin.site.register(User, UserAdmin)
