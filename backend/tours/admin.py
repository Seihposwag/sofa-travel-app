from django.contrib import admin

from .models import Country, Review, Tour


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["title", "created_at"]
    search_fields = ["title"]


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ["title", "country", "price", "duration_days", "author", "created_at"]
    list_filter = ["country"]
    list_editable = ["price"]
    search_fields = ["title", "description"]
    readonly_fields = ["created_at"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["tour", "author", "created_at"]
    search_fields = ["text"]
