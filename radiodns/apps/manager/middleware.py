import re

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


EXEMPT_URLS = [re.compile(settings.LOGIN_URL.lstrip("/"))]
if hasattr(settings, "SETUP_EXEMPT_URLS"):
    EXEMPT_URLS += [re.compile(url) for url in settings.SETUP_EXEMPT_URLS]


class SetupRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, "user"), "The Login Required Middleware"
        if request.user.is_authenticated:
            if (
                request.user.active_organization is None
                or request.user.active_organization.codops is None
            ):
                path = request.path_info.lstrip("/")
                if not any(m.match(path) for m in EXEMPT_URLS):
                    return HttpResponseRedirect(reverse("common:SetupErrorView"))
