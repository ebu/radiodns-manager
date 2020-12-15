from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.si_pi.si_pi_serving_provider.aws_serving import AWSServing
from apps.si_pi.si_pi_serving_provider.standalone_serving import StandaloneServing
from config.settings.base import SI_PI_SERVING_MODE


def get_serving_provider():
    if SI_PI_SERVING_MODE == "AWS":
        return AWSServing()
    else:
        return StandaloneServing()


def regenerate_si_pi():
    get_serving_provider().on_si_resource_changed()


@receiver(post_save, sender=MyModel)
def my_handler(sender, **kwargs):
