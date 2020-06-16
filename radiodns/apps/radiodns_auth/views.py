from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from social_django.utils import load_strategy, load_backend


def LoginView(request):
    form = AuthenticationForm()
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.data["username"], password=form.data["password"]
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("manager:details")
    context = {
        "form": form,
        "use_saml": settings.USE_SAML,
        "use_login": settings.USE_LOGIN,
    }
    return render(request, "radiodns_auth/login.html", context=context)


def LogoutView(request):
    logout(request)
    return redirect("radiodns_auth:login")


def SamlMetadataView(request):
    complete_url = redirect('social:complete', "saml")
    saml_backend = load_backend(
        load_strategy(request),
        "saml",
        redirect_uri=complete_url,
    )
    metadata, errors = saml_backend.generate_metadata_xml()
    if not errors:
        return HttpResponse(content=metadata, content_type='text/xml')
