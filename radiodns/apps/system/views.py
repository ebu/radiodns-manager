from django.shortcuts import render

from apps.awsutils import awsutils


def SystemStatusView(request):
    return render(request, "system/home.html")


def SystemCheckView(request):
    return awsutils.check_mainzone()
