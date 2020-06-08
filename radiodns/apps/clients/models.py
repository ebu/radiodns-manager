from django.db import models

from apps.manager.models import Organization


class Client(models.Model):
    name = models.CharField(max_length=500)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=128)
    email = models.EmailField()

    @classmethod
    def all_clients_in_organization(cls, organization_id):
        return list(cls.objects.filter(organization__id=organization_id))
