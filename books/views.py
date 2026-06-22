from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Book
from .permissions import IsOwner
from .serializers import (
    BookSerializer,
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
)


class BookViewSet(viewsets.ModelViewSet):
    """CRUD des livres. Endpoint protege : chaque utilisateur ne voit que ses livres."""

    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Vision differente par utilisateur : on filtre par proprietaire.
        return Book.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class RegisterView(generics.CreateAPIView):
    """Inscription publique d'un nouvel utilisateur."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ChangePasswordView(APIView):
    """Changement de mot de passe (utilisateur authentifie)."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @extend_schema(request=ChangePasswordSerializer, responses=ChangePasswordSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"old_password": "Mot de passe actuel incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Mot de passe modifie avec succes."})


class PasswordResetRequestView(APIView):
    """Esqueci minha senha : envoie un email avec un lien de reinitialisation."""

    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetRequestSerializer

    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses=PasswordResetRequestSerializer,
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()
        # On repond toujours 200 pour ne pas reveler l'existence d'un compte.
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"{settings.FRONTEND_URL}/reset-password.html?uid={uid}&token={token}"
            send_mail(
                subject="Reinitialisation de votre mot de passe",
                message=f"Cliquez sur ce lien pour reinitialiser votre mot de passe :\n{reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        return Response(
            {"detail": "Si un compte existe, un email a ete envoye."}
        )


class PasswordResetConfirmView(APIView):
    """Confirme la reinitialisation avec uid + token recus par email."""

    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses=PasswordResetConfirmSerializer,
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data["uid"]))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response(
                {"detail": "Lien invalide."}, status=status.HTTP_400_BAD_REQUEST
            )
        if not default_token_generator.check_token(
            user, serializer.validated_data["token"]
        ):
            return Response(
                {"detail": "Token invalide ou expire."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Mot de passe reinitialise avec succes."})
