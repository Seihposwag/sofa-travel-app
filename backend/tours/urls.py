from django.urls import path

from . import views

app_name = "tours"

urlpatterns = [
    path("", views.tour_list, name="tour_list"),
    path("country/<int:pk>/", views.tours_by_country, name="tours_by_country"),
    path("tour/new/", views.tour_create, name="tour_create"),
    path("tour/<int:pk>/", views.tour_detail, name="tour_detail"),
    path("tour/<int:pk>/edit/", views.tour_update, name="tour_update"),
    path("tour/<int:pk>/delete/", views.tour_delete, name="tour_delete"),
    path("ajax/review/<int:pk>/", views.review_add_ajax, name="review_add_ajax"),
]
