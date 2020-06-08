from django.shortcuts import render, get_object_or_404, redirect

from apps.clients.forms import ClientForm
from apps.clients.models import Client


def ListClientsView(request):
    clients = Client.objects.filter(
        organization__id=request.user.active_organization.id
    )
    return render(request, "clients/home.html", context={"clients": clients})


def EditClientView(request, client_id=None):
    client = None
    if client_id is not None:
        client = get_object_or_404(
            Client, id=client_id, organization__id=request.user.active_organization.id
        )
    form = ClientForm(instance=client)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            client = form.save(commit=False)
            client.organization = request.user.active_organization
            client.save()
            return redirect("clients:list")
    return render(request, "clients/edit.html", context={"form": form})


def DeleteClientView(request, client_id):
    client = get_object_or_404(
        Client, id=client_id, organization__id=request.user.active_organization.id
    )
    client.delete()
    return redirect("clients:list")
