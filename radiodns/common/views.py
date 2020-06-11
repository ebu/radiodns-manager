from django.shortcuts import render
from sentry_sdk import capture_message


def TermsView(request):
    return render(request, "terms.html")


def SetupErrorView(request):
    return render(request, "errors/setup_error.html")


def handler404(request, *args, **argv):
    response = render(request, "errors/404.html")
    response.status_code = 404
    return response


def handler403(request, *args, **argv):
    response = render(request, "errors/403.html")
    response.status_code = 403
    return response


def handler500(request, *args, **argv):
    response = render(request, "errors/500.html")
    response.status_code = 500
    return response
