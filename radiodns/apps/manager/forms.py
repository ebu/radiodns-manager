from django.forms import ModelForm, forms, ChoiceField, Select

from apps.manager.models import Organization


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
            "keywords",
        ]
