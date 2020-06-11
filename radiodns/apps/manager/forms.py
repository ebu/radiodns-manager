from django.forms import ModelForm, CharField

from apps.manager.models import Organization, LogoImage


class OrganizationForm(ModelForm):
    class Meta:
        model = Organization
        fields = [
            "short_name",
            "medium_name",
            "long_name",
            "long_description",
            "short_description",
            "url_default",
            "default_language",
            "location_country",
            "postal_name",
            "street",
            "city",
            "zipcode",
            "phone_number",
        ]


class LogoImageForm(ModelForm):
    replace_size = CharField(
        label="Replace particular size", max_length=10, required=False
    )

    class Meta:
        model = LogoImage
        fields = ["name", "file"]
