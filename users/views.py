from dj_rest_auth import app_settings
from dj_rest_auth.registration.views import VerifyEmailView
from django.shortcuts import render


# Create your views here.
class VerifyEmailOwn(VerifyEmailView):
    def send_email(self, *args, **kwargs):
        # Custom logic to send email verification email
        # You can modify the email content, subject, or any other aspect of the email here
        super().send_email(*args, **kwargs)
