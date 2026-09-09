from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from .forms import ReviewForm, TourForm
from .models import Country, Tour

TOURS_ON_PAGE = 6


def tour_list(request):
    tours = Tour.objects.select_related("country", "author")

    # поиск по названию и описанию
    query = request.GET.get("q", "")
    if query:
        tours = tours.filter(Q(title__icontains=query) | Q(description__icontains=query))

    paginator = Paginator(tours, TOURS_ON_PAGE)
    page = paginator.get_page(request.GET.get("page"))

    return render(request, "tours/tour_list.html", {
        "page_obj": page,
        "query": query,
        "countries": Country.objects.all(),
        "page_title": "Каталог туров",
    })


def tours_by_country(request, pk):
    country = get_object_or_404(Country, pk=pk)
    tours = Tour.objects.filter(country=country).select_related("author")

    paginator = Paginator(tours, TOURS_ON_PAGE)
    page = paginator.get_page(request.GET.get("page"))

    return render(request, "tours/tour_list.html", {
        "page_obj": page,
        "country": country,
        "countries": Country.objects.all(),
        "page_title": "Туры: " + country.title,
    })


def tour_detail(request, pk):
    tour = get_object_or_404(Tour.objects.select_related("country", "author"), pk=pk)

    can_edit = request.user.is_authenticated and (
        request.user == tour.author or request.user.is_staff
    )

    return render(request, "tours/tour_detail.html", {
        "tour": tour,
        "reviews": tour.reviews.select_related("author"),
        "review_form": ReviewForm(),
        "can_edit": can_edit,
        "page_title": tour.title,
    })


@login_required
def tour_create(request):
    if request.method == "POST":
        form = TourForm(request.POST, request.FILES)
        if form.is_valid():
            tour = form.save(commit=False)
            tour.author = request.user
            tour.save()
            messages.success(request, "Тур добавлен.")
            return redirect(tour.get_absolute_url())
    else:
        form = TourForm()

    return render(request, "tours/tour_form.html", {
        "form": form,
        "page_title": "Новый тур",
        "submit_label": "Добавить",
    })


@login_required
def tour_update(request, pk):
    tour = get_object_or_404(Tour, pk=pk)

    if request.user != tour.author and not request.user.is_staff:
        messages.error(request, "Можно менять только свои туры.")
        return redirect(tour.get_absolute_url())

    if request.method == "POST":
        form = TourForm(request.POST, request.FILES, instance=tour)
        if form.is_valid():
            form.save()
            messages.success(request, "Изменения сохранены.")
            return redirect(tour.get_absolute_url())
    else:
        form = TourForm(instance=tour)

    return render(request, "tours/tour_form.html", {
        "form": form,
        "tour": tour,
        "page_title": "Редактирование тура",
        "submit_label": "Сохранить",
    })


@login_required
def tour_delete(request, pk):
    tour = get_object_or_404(Tour, pk=pk)

    if request.user != tour.author and not request.user.is_staff:
        messages.error(request, "Можно удалять только свои туры.")
        return redirect(tour.get_absolute_url())

    if request.method == "POST":
        tour.delete()
        messages.success(request, "Тур удалён.")
        return redirect("tours:tour_list")

    return render(request, "tours/tour_confirm_delete.html", {
        "tour": tour,
        "page_title": "Удаление тура",
    })


# отзыв добавляется без перезагрузки страницы
@login_required
def review_add_ajax(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    form = ReviewForm(request.POST)

    if not form.is_valid():
        return JsonResponse({"ok": False, "error": "Отзыв слишком короткий."}, status=400)

    review = form.save(commit=False)
    review.tour = tour
    review.author = request.user
    review.save()

    html = render_to_string("inc/review.html", {"review": review})
    return JsonResponse({"ok": True, "html": html, "total": tour.reviews.count()})
