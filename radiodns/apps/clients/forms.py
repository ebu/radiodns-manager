from django.forms import ModelForm

from apps.clients.models import Client


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ["name", "email", "identifier"]
