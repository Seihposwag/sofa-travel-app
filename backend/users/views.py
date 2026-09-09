"""
Представления приложения users.

Реализована сессионная аутентификация на встроенных механизмах Django:
регистрация, вход, выход и просмотр с редактированием профиля.
Идентификатор сессии передаётся в cookie, формы защищены csrf-токеном.
"""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render

from .forms import LoginForm, ProfileUpdateForm, RegisterForm


def register(request):
    """Регистрация нового пользователя с автоматическим входом."""
    if request.user.is_authenticated:
        return redirect("tours:tour_list")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Добро пожаловать, {user.display_name}!")
        return redirect("tours:tour_list")

    return render(
        request,
        "users/register.html",
        {"form": form, "page_title": "Регистрация"},
    )


def user_login(request):
    """Вход в систему по логину и паролю."""
    if request.user.is_authenticated:
        return redirect("tours:tour_list")

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        if user is not None:
            login(request, user)
            messages.success(request, f"Вы вошли как {user.display_name}.")
            return redirect(request.GET.get("next") or "tours:tour_list")
        messages.error(request, "Неверное имя пользователя или пароль.")

    return render(
        request,
        "users/login.html",
        {"form": form, "page_title": "Вход"},
    )


def user_logout(request):
    """Выход из системы и завершение сессии."""
    logout(request)
    messages.info(request, "Вы вышли из системы.")
    return redirect("tours:tour_list")


@login_required
def profile(request):
    """Просмотр и редактирование личных данных."""
    form = ProfileUpdateForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Профиль обновлён.")
        return redirect("users:profile")

    stats = request.user.tours.aggregate(
        tours_total=Count("id"),
    )

    return render(
        request,
        "users/profile.html",
        {
            "form": form,
            "tours_total": stats["tours_total"],
            "favorites_total": request.user.favorites.count(),
            "reviews_total": request.user.reviews.count(),
            "page_title": "Профиль",
        },
    )
