"""Commande de peuplement (seed) de la base avec des donnees d'exemple.

Idempotente : on peut la lancer plusieurs fois sans creer de doublons
(les utilisateurs, livres, avis... sont recuperes ou crees via get_or_create).

Usage :
    python manage.py seed
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from books.models import Book, Loan, Reservation, Review


class Command(BaseCommand):
    help = "Peuple la base avec des utilisateurs, livros, avaliacoes, emprestimos."

    def handle(self, *args, **options):
        # --- Utilisateurs ---------------------------------------------------
        users = {}
        for username, is_staff in [
            ("admin", True),
            ("theo", False),
            ("lucie", False),
            ("carlos", False),
        ]:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@biblioteca.local",
                    "is_staff": is_staff,
                    "is_superuser": is_staff,
                },
            )
            if created:
                user.set_password("Senha12345")
                user.save()
            users[username] = user

        # --- Livres ---------------------------------------------------------
        # (titre, auteur, description, proprietaire, status, exemplaires)
        books_data = [
            ("Dom Casmurro", "Machado de Assis",
             "Romance classico da literatura brasileira.", "admin",
             Book.APPROVED, 3),
            ("Capitães da Areia", "Jorge Amado",
             "A vida de meninos de rua em Salvador.", "admin",
             Book.APPROVED, 2),
            ("Grande Sertão: Veredas", "João Guimarães Rosa",
             "Obra-prima da prosa brasileira.", "admin",
             Book.APPROVED, 1),
            ("A Hora da Estrela", "Clarice Lispector",
             "A historia de Macabea.", "theo",
             Book.APPROVED, 2),
            ("O Cortiço", "Aluísio Azevedo",
             "Romance naturalista.", "lucie",
             Book.APPROVED, 2),
            ("Vidas Secas", "Graciliano Ramos",
             "A seca e a miseria no sertao nordestino.", "carlos",
             Book.PENDING, 1),
            ("Memórias Póstumas de Brás Cubas", "Machado de Assis",
             "Narrado por um defunto autor.", "theo",
             Book.PENDING, 1),
        ]
        books = {}
        for title, author, desc, owner, status, copies in books_data:
            book, _ = Book.objects.get_or_create(
                title=title,
                created_by=users[owner],
                defaults={
                    "author": author,
                    "description": desc,
                    "status": status,
                    "total_copies": copies,
                },
            )
            books[title] = book

        # --- Avaliacoes -----------------------------------------------------
        reviews_data = [
            ("Dom Casmurro", "theo", 5, "Imperdivel! Sera que a Capitu traiu?"),
            ("Dom Casmurro", "lucie", 4, "Muito bom, leitura obrigatoria."),
            ("Capitães da Areia", "carlos", 5, "Emocionante do inicio ao fim."),
            ("A Hora da Estrela", "lucie", 4, "Curto e profundo."),
            ("O Cortiço", "theo", 3, "Interessante, mas denso."),
        ]
        for title, author, rating, comment in reviews_data:
            Review.objects.get_or_create(
                book=books[title],
                author=users[author],
                defaults={"rating": rating, "comment": comment},
            )

        # --- Emprestimo (theo pegou um livro) -------------------------------
        Loan.objects.get_or_create(
            book=books["Capitães da Areia"],
            user=users["theo"],
            status=Loan.ACTIVE,
            defaults={"due_date": timezone.now().date() + timedelta(days=14)},
        )

        # --- Reserva (lucie na fila de um livro com 1 exemplar) -------------
        Reservation.objects.get_or_create(
            book=books["Grande Sertão: Veredas"],
            user=users["lucie"],
            status=Reservation.WAITING,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed concluido: {User.objects.count()} usuarios, "
                f"{Book.objects.count()} livros, {Review.objects.count()} avaliacoes."
            )
        )
