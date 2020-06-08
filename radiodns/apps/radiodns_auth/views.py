from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.conf import settings


def login_view(request):
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


def logout_view(request):
    logout(request)
    return redirect("radiodns_auth:login")
