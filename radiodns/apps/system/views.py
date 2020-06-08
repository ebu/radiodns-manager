from django.shortcuts import render


def SystemStatusView(request):
    return render(request, "system/home.html")
