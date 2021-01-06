from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.manager.models import Organization


class User(AbstractUser):

    current_organization = models.ForeignKey(
        Organization, null=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.email}"

    @property
    def organizations_list(self):
        if self.is_superuser:
            return list(Organization.objects.all())
        return list(self.organization_set.all())

    @property
    def active_organization(self):
        if not self.current_organization:
            if self.is_superuser:
                self.current_organization = Organization.objects.first()
            else:
                self.current_organization = self.organization_set.first()
        return self.current_organization

    @active_organization.setter
    def active_organization(self, organization):
        self.current_organization = organization
