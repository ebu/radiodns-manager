from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from lpp_core.models import LppUser, Organization


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = LppUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):
    organization = forms.ModelChoiceField(queryset=Organization.objects.all(), required=False)

    class Meta:
        model = LppUser
        fields = ('username', 'email', "organization")
