from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    """Livre appartenant a un utilisateur (catalogue personnel)."""

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="books"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
