from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from apps.clients.forms import ClientForm
from apps.clients.models import Client


@login_required
def list_clients(request):
    clients = Client.objects.filter(
        organization__id=request.user.active_organization.id
    )
    return render(request, "clients/home.html", context={"clients": clients})


@login_required
def edit_client(request, client_id=None):
    client = None
    if client_id is not None:
        client = get_object_or_404(Client, id=client_id)
    form = ClientForm(instance=client)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect("clients:list")
    return render(request, "clients/edit.html", context={"form": form})


@login_required
def delete_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.delete()
    client.save()
    return redirect("clients:list")
