from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BookViewSet,
    ChangePasswordView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
)

router = DefaultRouter()
router.register(r"books", BookViewSet, basename="book")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path(
        "auth/password-reset/",
        PasswordResetRequestView.as_view(),
        name="password-reset",
    ),
    path(
        "auth/password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]
