"""Настройка админ-панели для приложения tours."""

from django.contrib import admin

from .models import Country, Favorite, Review, Tour


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "published_tours_count", "created_at")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("title",)


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ("author", "text", "is_active", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "country",
        "price",
        "duration_days",
        "author",
        "is_published",
        "views",
        "created_at",
    )
    list_filter = ("is_published", "country", "created_at")
    list_editable = ("is_published", "price")
    search_fields = ("title", "description")
    date_hierarchy = "created_at"
    readonly_fields = ("views", "created_at", "updated_at")
    autocomplete_fields = ("country",)
    inlines = (ReviewInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("country", "author")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("tour", "author", "created_at", "is_active")
    list_filter = ("is_active", "created_at")
    search_fields = ("text", "author__username", "tour__title")
    list_editable = ("is_active",)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "tour", "created_at")
    search_fields = ("user__username", "tour__title")
