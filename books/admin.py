from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "read", "owner", "created_at")
    list_filter = ("read", "owner")
    search_fields = ("title", "author")
