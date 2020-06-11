from django.forms import ModelForm

from apps.channels.models import Image


class ImageForm(ModelForm):
    class Meta:
        model = Image
        fields = ["name", "radiotext", "radiolink", "file"]
