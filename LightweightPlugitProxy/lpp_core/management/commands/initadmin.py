import os

from django.core.management.base import BaseCommand

from lpp_core.models import LppUser


class Command(BaseCommand):

    def handle(self, *args, **options):
        if LppUser.objects.count() == 0:
            username = os.environ.get("SU_NAME")
            email = os.environ.get("SU_EMAIL")
            password = os.environ.get("SU_PASSWORD")
            if username == "" or email == "" or password == "":
                raise EnvironmentError("Cannot create a user with blank values!")
            print('Creating account for %s (%s)' % (username, email))
            admin = LppUser.objects.create_superuser(email=email, username=username, password=password)
            admin.is_active = True
            admin.is_admin = True
            admin.save()
        else:
            print('Admin accounts can only be initialized if no Accounts exist')
