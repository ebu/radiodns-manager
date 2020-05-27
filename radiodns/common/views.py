from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    return render(request, "index.html")


def terms(request):
    return render(request, "terms.html")
