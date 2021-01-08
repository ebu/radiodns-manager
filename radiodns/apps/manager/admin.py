from django.contrib import admin

# Register your models here.
from apps.manager.models import Organization


class OrganizationAdminInline(admin.TabularInline):
    model = Organization.users.through
    show_change_link = True
    extra = 1


class OrganizationAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Codops", {"fields": ["codops"]}),
        ("Name", {"fields": ["short_name", "medium_name", "long_name"]}),
        ("Description", {"fields": ["short_description", "long_description"]}),
        ("Language", {"fields": ["default_language"]}),
        ("Links", {"fields": ["url_default"]}),
        (
            "Address",
            {
                "fields": [
                    "postal_name",
                    "street",
                    "city",
                    "zipcode",
                    "location_country",
                    "phone_number",
                ]
            },
        ),
        ("Users", {"fields": ["users"]}),
        ("Logo", {"fields": ["default_image_id"]}),
    ]
    filter_horizontal = ('users',)
    list_display = (
        "medium_name",
        "long_name",
        "short_description",
        "url_default",
        "default_language",
        "location_country",
    )


admin.site.register(Organization, OrganizationAdmin)
