from django.contrib import admin

# Register your models here.
from apps.channels.models import Channel

admin.site.register(Channel)
