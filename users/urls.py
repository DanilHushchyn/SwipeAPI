# from allauth.account.views import ConfirmEmailView
# from dj_rest_auth.registration.views import VerifyEmailView
# from dj_rest_auth.views import (
#     LoginView,
#     LogoutView,
#     PasswordChangeView,
#     PasswordResetConfirmView,
#     PasswordResetView,
#     UserDetailsView,
# )
# from django.urls import include, path, re_path
# from rest_framework.routers import DefaultRouter
#
# from users.views import ProfileViewSet
#
# router = DefaultRouter()
# router.register(prefix=r"profiles", viewset=ProfileViewSet, basename="profiles")
#
# urlpatterns = [
#     # User Auth
#     path("login/", LoginView.as_view(), name="rest_login"),
#     path("logout/", LogoutView.as_view(), name="rest_logout"),
#     path(
#         "password/reset/",
#         PasswordResetView.as_view(),
#         name="rest_password_reset",
#     ),
#     path(
#         "password/reset/confirm/<uidb64>/<token>/",
#         PasswordResetConfirmView.as_view(),
#         name="rest_password_reset_confirm",
#     ),
#     path(
#         "password/change/",
#         PasswordChangeView.as_view(),
#         name="rest_password_change",
#     ),
#     path("user/", UserDetailsView.as_view(), name="user"),
#     path("registration/", include("dj_rest_auth.registration.urls")),
#     re_path(
#         r"^account-confirm-email/(?P<key>[-:\w]+)/$",
#         VerifyEmailView.as_view(),
#         name="account_confirm_email",
#     ),
#     path('', include(router.urls))
# ]


from allauth.account.views import ConfirmEmailView
from dj_rest_auth.registration.views import VerifyEmailView, ResendEmailVerificationView
from dj_rest_auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
    UserDetailsView,
)
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from users.views import ProfileViewSet, CustomRegisterView

router = DefaultRouter()
router.register(prefix=r"profiles", viewset=ProfileViewSet, basename="profiles")

urlpatterns = [
    # User Auth
    path("login/", LoginView.as_view(), name="rest_login"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path(
        "password/reset/",
        PasswordResetView.as_view(),
        name="rest_password_reset",
    ),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="rest_password_reset_confirm",
    ),
    path(
        "password/change/",
        PasswordChangeView.as_view(),
        name="rest_password_change",
    ),
    path("user/", UserDetailsView.as_view(), name="user"),
    path('registration/', CustomRegisterView.as_view(), name='rest_register'),
    path('registration/verify-email/', VerifyEmailView.as_view(), name='rest_verify_email'),
    path('registration/resend-email/', ResendEmailVerificationView.as_view(), name="rest_resend_email"),
    path(
        'account-email-verification-sent/', TemplateView.as_view(),
        name='account_email_verification_sent',
    ),
    re_path(
        r"^account-confirm-email/(?P<key>[-:\w]+)/$",
        VerifyEmailView.as_view(),
        name="account_confirm_email",
    ),
    path('', include(router.urls))
]
