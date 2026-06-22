from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Book, Review
from .permissions import IsOwnerOrAdmin
from .serializers import (
    BookSerializer,
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    ReviewSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Lister les livres",
        description=(
            "Administrateur : voit tous les livres (y compris en attente).\n"
            "Utilisateur normal : voit les livres approuves et ses propres "
            "soumissions en attente."
        ),
        tags=["books"],
    ),
    create=extend_schema(
        summary="Soumettre un livre",
        description=(
            "Un administrateur cree un livre directement approuve. "
            "Un utilisateur normal cree un livre en attente de validation."
        ),
        tags=["books"],
    ),
    retrieve=extend_schema(tags=["books"]),
    update=extend_schema(tags=["books"]),
    partial_update=extend_schema(tags=["books"]),
    destroy=extend_schema(tags=["books"]),
)
class BookViewSet(viewsets.ModelViewSet):
    """CRUD des livres de la bibliotheque communautaire."""

    serializer_class = BookSerializer

    def get_permissions(self):
        # Editer / supprimer : proprietaire ou admin. Valider : admin (gere
        # dans l'action). Le reste : utilisateur authentifie.
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # L'admin voit tout pour pouvoir moderer.
            return Book.objects.all()
        # L'utilisateur voit les livres approuves + ses propres soumissions.
        return Book.objects.filter(
            Q(status=Book.APPROVED) | Q(created_by=user)
        )

    def perform_create(self, serializer):
        # Un livre cree par un admin est approuve d'office.
        new_status = (
            Book.APPROVED if self.request.user.is_staff else Book.PENDING
        )
        serializer.save(created_by=self.request.user, status=new_status)

    @extend_schema(
        summary="Valider un livre (admin)",
        description="Approuve un livre en attente. Reserve aux administrateurs.",
        request=None,
        responses={200: BookSerializer},
        tags=["books"],
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAdminUser],
    )
    def approve(self, request, pk=None):
        book = self.get_object()
        book.status = Book.APPROVED
        book.save()
        return Response(self.get_serializer(book).data)


@extend_schema_view(
    list=extend_schema(summary="Lister les avis", tags=["reviews"]),
    create=extend_schema(summary="Deposer un avis", tags=["reviews"]),
    retrieve=extend_schema(tags=["reviews"]),
    update=extend_schema(tags=["reviews"]),
    partial_update=extend_schema(tags=["reviews"]),
    destroy=extend_schema(
        summary="Supprimer un avis",
        description="L'auteur de l'avis ou un administrateur peut le supprimer.",
        tags=["reviews"],
    ),
)
class ReviewViewSet(viewsets.ModelViewSet):
    """CRUD des avis. Filtrable par livre via `?book=<id>`."""

    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # On ne montre que les avis des livres approuves (ou tout pour l'admin).
        qs = Review.objects.select_related("book", "author")
        if not self.request.user.is_staff:
            qs = qs.filter(book__status=Book.APPROVED)
        book_id = self.request.query_params.get("book")
        if book_id:
            qs = qs.filter(book_id=book_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RegisterView(generics.CreateAPIView):
    """Inscription publique d'un nouvel utilisateur."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="Cadastro de usuario", tags=["auth"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ChangePasswordView(APIView):
    """Changement de mot de passe (utilisateur authentifie)."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @extend_schema(
        summary="Trocar senha",
        request=ChangePasswordSerializer,
        responses={200: OpenApiResponse(description="Mot de passe modifie.")},
        tags=["auth"],
    )
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
        summary="Esqueci minha senha",
        request=PasswordResetRequestSerializer,
        responses={200: OpenApiResponse(description="Email envoye si le compte existe.")},
        tags=["auth"],
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
        summary="Confirmar nova senha",
        request=PasswordResetConfirmSerializer,
        responses={200: OpenApiResponse(description="Mot de passe reinitialise.")},
        tags=["auth"],
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
