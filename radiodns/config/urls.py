"""radiodns URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.models import Group
from django.urls import include, path

admin.site.site_header = "RadioDNS Manager - Administration Panel"
admin.site.index_title = "Manage organizations and users"
admin.site.site_title = "HTML title from adminsitration"
admin.site.unregister(Group)


urlpatterns = [
    path("", include("common.urls")),
    path("", include("apps.manager.urls")),
    path("", include("apps.radiodns_auth.urls")),
    path("stations/", include("apps.stations.urls")),
    path("channels/", include("apps.channels.urls")),
    path("clients/", include("apps.clients.urls")),
    path("radiovis/", include("apps.radiovis.urls")),
    path("radioepg/", include("apps.radioepg.urls")),
    path("system/", include("apps.system.urls")),
    path("admin/", admin.site.urls),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
handler404 = "common.views.handler404"
handler403 = "common.views.handler403"
handler500 = "common.views.handler500"
