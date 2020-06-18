from django.forms import ModelForm

from apps.stations.models import Station, StationInstance


class StationForm(ModelForm):
    class Meta:
        model = Station
        fields = [
            "radiovis_enabled",
            "radiovis_service",
            "radioepg_enabled",
            "radioepg_service",
            "radiospi_service",
            "radioepgpi_enabled",
            "radiotag_enabled",
            "radiotag_service",
            "ip_allowed",
        ]


class StationInstanceForm(ModelForm):
    class Meta:
        model = StationInstance
        fields = [
            "name",
            "short_name",
            "medium_name",
            "long_name",
            "short_description",
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
            "default_language",
            "location_country",
        ]
