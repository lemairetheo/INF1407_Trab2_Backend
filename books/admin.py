from django.contrib import admin

from .models import Book, Loan, Reservation, Review


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "created_by", "created_at")
    list_filter = ("status", "created_by")
    search_fields = ("title", "author")
    actions = ["approve_books"]

    @admin.action(description="Aprovar livros selecionados")
    def approve_books(self, request, queryset):
        queryset.update(status=Book.APPROVED)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("book", "author", "rating", "created_at")
    list_filter = ("rating", "author")
    search_fields = ("comment",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "borrowed_at", "due_date", "status")
    list_filter = ("status", "user")
    search_fields = ("book__title", "user__username")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "created_at", "status")
    list_filter = ("status", "user")
    search_fields = ("book__title", "user__username")
