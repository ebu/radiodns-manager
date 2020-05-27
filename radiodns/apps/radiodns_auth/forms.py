from django.contrib.auth.forms import AuthenticationForm


class UserAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        pass
