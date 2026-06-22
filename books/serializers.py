from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Book, Loan, Reservation, Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serialise un avis. author est rempli a partir de l'utilisateur connecte."""

    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Review
        fields = ["id", "book", "author", "rating", "comment", "created_at"]


class BookSerializer(serializers.ModelSerializer):
    """Serialise un livre. status et created_by sont en lecture seule."""

    created_by = serializers.ReadOnlyField(source="created_by.username")
    reviews = ReviewSerializer(many=True, read_only=True)
    available_copies = serializers.ReadOnlyField()

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "description",
            "status",
            "total_copies",
            "available_copies",
            "created_by",
            "created_at",
            "reviews",
        ]
        read_only_fields = ["status", "created_by"]


class LoanSerializer(serializers.ModelSerializer):
    """Serialise un emprunt avec quelques infos du livre et de l'utilisateur."""

    user = serializers.ReadOnlyField(source="user.username")
    book_title = serializers.ReadOnlyField(source="book.title")

    class Meta:
        model = Loan
        fields = [
            "id",
            "book",
            "book_title",
            "user",
            "borrowed_at",
            "due_date",
            "returned_at",
            "status",
        ]
        read_only_fields = fields


class ReservationSerializer(serializers.ModelSerializer):
    """Serialise une reservation (file d'attente)."""

    user = serializers.ReadOnlyField(source="user.username")
    book_title = serializers.ReadOnlyField(source="book.title")

    class Meta:
        model = Reservation
        fields = [
            "id",
            "book",
            "book_title",
            "user",
            "created_at",
            "status",
        ]
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    """Inscription d'un nouvel utilisateur."""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Changement de mot de passe pour un utilisateur authentifie."""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True, validators=[validate_password]
    )


class PasswordResetRequestSerializer(serializers.Serializer):
    """Demande de reinitialisation : on envoie un email avec un lien."""

    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Confirmation de la reinitialisation avec le token recu par email."""

    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True, validators=[validate_password]
    )
