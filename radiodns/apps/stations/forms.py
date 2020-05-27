from django.forms import ModelForm

from apps.stations.models import Station


class StationForm(ModelForm):
    class Meta:
        model = Station
        fields = [
            "name",
            "short_name",
            "medium_name",
            "long_name",
            "short_description",
            "long_description",
            "url_default",
            "postal_name",
            "street",
            "city",
            "zipcode",
            "phone_number",
            "sms_number",
            "sms_body",
            "sms_description",
            "email_address",
            "email_description",
            "keywords",
            "default_language",
            "location_country",
            "genres",
        ]
