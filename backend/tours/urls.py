"""Маршруты приложения tours."""

from django.urls import path

from . import views

app_name = "tours"

urlpatterns = [
    path("", views.tour_list, name="tour_list"),
    path("countries/", views.country_list, name="country_list"),
    path("country/<slug:slug>/", views.tours_by_country, name="tours_by_country"),
    path("tour/<int:pk>/", views.tour_detail, name="tour_detail"),
    path("tour/new/", views.tour_create, name="tour_create"),
    path("tour/<int:pk>/edit/", views.tour_update, name="tour_update"),
    path("tour/<int:pk>/delete/", views.tour_delete, name="tour_delete"),
    path("my/", views.my_tours, name="my_tours"),
    path("favorites/", views.favorites_list, name="favorites_list"),
    # AJAX
    path("ajax/tour/<int:pk>/review/", views.review_add_ajax, name="review_add_ajax"),
    path("ajax/tour/<int:pk>/favorite/", views.favorite_toggle_ajax, name="favorite_toggle_ajax"),
    path("ajax/search/", views.search_suggest_ajax, name="search_suggest_ajax"),
]
