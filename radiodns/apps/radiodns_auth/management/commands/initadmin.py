import os

from django.core.management.base import BaseCommand

from apps.radiodns_auth.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        if User.objects.count() == 0:
            username = os.environ.get("SU_NAME", "admin")
            email = os.environ.get("SU_EMAIL", "admin@gmail.com")
            password = os.environ.get("SU_PASSWORD", "admin")
            admin = User.objects.create_superuser(
                email=email, username=username, password=password
            )
            admin.save()
            print("Created default admin account")
        else:
            print("Admin accounts can only be initialized if no Accounts exist")
