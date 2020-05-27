from django.contrib import admin

# Register your models here.
from apps.manager.models import Organization

admin.site.register(Organization)
