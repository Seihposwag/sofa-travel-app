"""
Представления приложения tours.

Публичная часть доступна всем: список туров с пагинацией, отбор по
направлению, детальный просмотр и поиск. Приватная часть требует
авторизации: создание туров, редактирование и удаление своих,
отзывы и избранное. Обработчики с суффиксом _ajax отвечают
на асинхронные запросы и возвращают JSON.
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from .forms import ReviewForm, TourForm
from .models import Country, Favorite, Tour


def _published_tours():
    """Базовый набор опубликованных туров с подгруженными связями."""
    return (
        Tour.objects.filter(is_published=True)
        .select_related("country", "author")
        .annotate(reviews_total=Count("reviews", filter=Q(reviews__is_active=True)))
        .order_by("-created_at")
    )


def _paginate(request, queryset):
    """Разбивает набор объектов на страницы согласно настройке PAGINATE_BY."""
    paginator = Paginator(queryset, settings.PAGINATE_BY)
    return paginator.get_page(request.GET.get("page"))


def _can_edit(user, tour):
    """Редактировать тур может его автор или администратор."""
    return user.is_authenticated and (user == tour.author or user.is_staff)


# --------------------------------------------------------------- публичная часть


def tour_list(request):
    """Главная страница: каталог туров с пагинацией и поиском."""
    query = request.GET.get("q", "").strip()
    tours = _published_tours()

    if query:
        tours = tours.filter(Q(title__icontains=query) | Q(description__icontains=query))

    return render(
        request,
        "tours/tour_list.html",
        {
            "page_obj": _paginate(request, tours),
            "query": query,
            "countries": Country.objects.annotate(total=Count("tours")),
            "page_title": "Каталог туров",
        },
    )


def tours_by_country(request, slug):
    """Туры выбранного направления."""
    country = get_object_or_404(Country, slug=slug)
    tours = _published_tours().filter(country=country)

    return render(
        request,
        "tours/tour_list.html",
        {
            "page_obj": _paginate(request, tours),
            "country": country,
            "countries": Country.objects.annotate(total=Count("tours")),
            "page_title": f"Туры: {country.title}",
        },
    )


def country_list(request):
    """Все направления бюро с количеством предложений."""
    countries = Country.objects.annotate(total=Count("tours")).order_by("title")
    return render(
        request,
        "tours/country_list.html",
        {"countries": countries, "page_title": "Направления"},
    )


def tour_detail(request, pk):
    """Детальный просмотр тура: описание, отзывы и форма нового отзыва."""
    tour = get_object_or_404(
        Tour.objects.select_related("country", "author"),
        pk=pk,
    )

    if not tour.is_published and not _can_edit(request.user, tour):
        messages.warning(request, "Этот тур снят с публикации.")
        return redirect("tours:tour_list")

    # Инкремент на стороне БД исключает потерю просмотров при
    # одновременных запросах, refresh_from_db возвращает актуальное значение.
    Tour.objects.filter(pk=tour.pk).update(views=F("views") + 1)
    tour.refresh_from_db(fields=["views"])

    in_favorites = (
        request.user.is_authenticated
        and Favorite.objects.filter(user=request.user, tour=tour).exists()
    )

    return render(
        request,
        "tours/tour_detail.html",
        {
            "tour": tour,
            "reviews": tour.reviews.filter(is_active=True).select_related("author"),
            "review_form": ReviewForm(),
            "in_favorites": in_favorites,
            "can_edit": _can_edit(request.user, tour),
            "page_title": tour.title,
        },
    )


# --------------------------------------------------------------- приватная часть


@login_required
def tour_create(request):
    """Создание нового туристического предложения."""
    form = TourForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        tour = form.save(commit=False)
        tour.author = request.user
        tour.save()
        messages.success(request, "Тур опубликован.")
        return redirect(tour.get_absolute_url())

    return render(
        request,
        "tours/tour_form.html",
        {"form": form, "page_title": "Новый тур", "submit_label": "Опубликовать"},
    )


@login_required
def tour_update(request, pk):
    """Редактирование своего тура."""
    tour = get_object_or_404(Tour, pk=pk)

    if not _can_edit(request.user, tour):
        messages.error(request, "Редактировать можно только свои туры.")
        return redirect(tour.get_absolute_url())

    form = TourForm(request.POST or None, request.FILES or None, instance=tour)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Изменения сохранены.")
        return redirect(tour.get_absolute_url())

    return render(
        request,
        "tours/tour_form.html",
        {
            "form": form,
            "tour": tour,
            "page_title": "Редактирование тура",
            "submit_label": "Сохранить",
        },
    )


@login_required
def tour_delete(request, pk):
    """Удаление своего тура с подтверждением."""
    tour = get_object_or_404(Tour, pk=pk)

    if not _can_edit(request.user, tour):
        messages.error(request, "Удалять можно только свои туры.")
        return redirect(tour.get_absolute_url())

    if request.method == "POST":
        tour.delete()
        messages.success(request, "Тур удалён.")
        return redirect("tours:tour_list")

    return render(
        request,
        "tours/tour_confirm_delete.html",
        {"tour": tour, "page_title": "Удаление тура"},
    )


@login_required
def my_tours(request):
    """Туры, опубликованные текущим пользователем."""
    tours = (
        Tour.objects.filter(author=request.user)
        .select_related("country")
        .annotate(reviews_total=Count("reviews"))
        .order_by("-created_at")
    )
    return render(
        request,
        "tours/my_tours.html",
        {"page_obj": _paginate(request, tours), "page_title": "Мои туры"},
    )


@login_required
def favorites_list(request):
    """Избранные туры текущего пользователя."""
    tours = _published_tours().filter(favorites__user=request.user)
    return render(
        request,
        "tours/tour_list.html",
        {
            "page_obj": _paginate(request, tours),
            "countries": Country.objects.annotate(total=Count("tours")),
            "page_title": "Избранное",
            "empty_hint": "Вы пока не добавили ни одного тура в избранное.",
        },
    )


# --------------------------------------------------------------- AJAX-обработчики


@login_required
@require_POST
def review_add_ajax(request, pk):
    """Добавление отзыва без перезагрузки страницы."""
    tour = get_object_or_404(Tour, pk=pk)
    form = ReviewForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {"ok": False, "errors": form.errors.get("text", ["Проверьте текст отзыва."])},
            status=400,
        )

    review = form.save(commit=False)
    review.tour = tour
    review.author = request.user
    review.save()

    return JsonResponse(
        {
            "ok": True,
            "html": render_to_string("inc/review.html", {"review": review}, request),
            "total": tour.reviews_count,
        }
    )


@login_required
@require_POST
def favorite_toggle_ajax(request, pk):
    """Переключение тура в избранном без перезагрузки страницы."""
    tour = get_object_or_404(Tour, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, tour=tour)

    if not created:
        favorite.delete()

    return JsonResponse({"ok": True, "in_favorites": created})


def search_suggest_ajax(request):
    """Подсказки поиска по мере ввода."""
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return JsonResponse({"results": []})

    tours = (
        _published_tours()
        .filter(Q(title__icontains=query) | Q(country__title__icontains=query))
        .order_by("title")[:6]
    )

    return JsonResponse(
        {
            "results": [
                {
                    "title": tour.title,
                    "country": tour.country.title,
                    "price": f"{tour.price:.0f}",
                    "url": tour.get_absolute_url(),
                }
                for tour in tours
            ]
        }
    )
