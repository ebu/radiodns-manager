from django.forms import ModelForm, CharField

from apps.radioepg.models import Show, GenericServiceFollowingEntry as Service


class ShowForm(ModelForm):
    class Meta:
        model = Show
        fields = ["medium_name", "long_name", "description", "color"]


class ServiceForm(ModelForm):
    class Meta:
        model = Service
        fields = [
            "channel",
            "cost",
            "mime_type",
            "offset",
            "bitrate",
        ]
