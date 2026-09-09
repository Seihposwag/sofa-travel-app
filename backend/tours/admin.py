from django.contrib import admin

from .models import Country, Favorite, Review, Tour


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["title", "created_at"]
    search_fields = ["title"]


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ["title", "country", "price", "duration_days", "author", "is_published", "views"]
    list_filter = ["is_published", "country"]
    list_editable = ["price", "is_published"]
    search_fields = ["title", "description"]
    readonly_fields = ["views", "created_at", "updated_at"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["tour", "author", "created_at", "is_active"]
    list_filter = ["is_active"]
    list_editable = ["is_active"]
    search_fields = ["text"]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["user", "tour", "created_at"]
