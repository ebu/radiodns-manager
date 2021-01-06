from django.contrib import admin

from apps.channels.models import Channel


class ChannelAdminInline(admin.TabularInline):
    model = Channel
