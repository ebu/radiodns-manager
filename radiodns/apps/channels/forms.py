from django.forms import ModelForm

from .models import Channel


class ChannelForm(ModelForm):
    class Meta:
        model = Channel
        fields = [
            "name",
            "station",
            "type_id",
            "pi",
            "frequency",
            "eid",
            "sid",
            "scids",
            "appty_uatype",
            "pa",
            "stream_url",
            "bitrate",
            "mime_type",
            "tx",
            "ecc",
            "mid",
            "fqdn",
            "serviceIdentifier",
        ]
