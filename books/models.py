from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Book(models.Model):
    """Livre d'une bibliotheque communautaire.

    Un livre cree par un administrateur est immediatement approuve.
    Un livre cree par un utilisateur normal reste en attente (PENDING)
    jusqu'a ce qu'un administrateur le valide (APPROVED).
    """

    PENDING = "pending"
    APPROVED = "approved"
    STATUS_CHOICES = [
        (PENDING, "Em analise"),
        (APPROVED, "Aprovado"),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=PENDING
    )
    total_copies = models.PositiveSmallIntegerField(default=1)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="books"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def active_loans_count(self):
        return self.loans.filter(status=Loan.ACTIVE).count()

    @property
    def available_copies(self):
        """Nombre d'exemplaires disponibles a l'emprunt."""
        return max(self.total_copies - self.active_loans_count, 0)


class Review(models.Model):
    """Avis laisse par un utilisateur sur un livre.

    Tout utilisateur authentifie peut deposer un avis.
    L'auteur de l'avis ou un administrateur peut le supprimer.
    """

    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="reviews"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        # Un utilisateur ne peut laisser qu'un seul avis par livre.
        unique_together = ("book", "author")

    def __str__(self):
        return f"{self.author.username} -> {self.book.title} ({self.rating}/5)"


class Loan(models.Model):
    """Emprunt d'un exemplaire de livre par un utilisateur."""

    ACTIVE = "active"
    RETURNED = "returned"
    STATUS_CHOICES = [
        (ACTIVE, "Em andamento"),
        (RETURNED, "Devolvido"),
    ]

    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="loans"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="loans"
    )
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=ACTIVE
    )

    class Meta:
        ordering = ["-borrowed_at"]

    def __str__(self):
        return f"{self.user.username} -> {self.book.title} ({self.status})"


class Reservation(models.Model):
    """Reservation (file d'attente) quand un livre n'a plus d'exemplaire libre."""

    WAITING = "waiting"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (WAITING, "Na fila"),
        (FULFILLED, "Disponivel"),
        (CANCELLED, "Cancelada"),
    ]

    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="reservations"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reservations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=WAITING
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username} reservou {self.book.title} ({self.status})"
