from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BookViewSet,
    ChangePasswordView,
    LoanViewSet,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    ReservationViewSet,
    ReviewViewSet,
)

router = DefaultRouter()
router.register(r"books", BookViewSet, basename="book")
router.register(r"reviews", ReviewViewSet, basename="review")
router.register(r"loans", LoanViewSet, basename="loan")
router.register(r"reservations", ReservationViewSet, basename="reservation")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/me/", MeView.as_view(), name="me"),
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
