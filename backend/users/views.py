from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, ProfileForm, RegisterForm


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно.")
            return redirect("tours:tour_list")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {
        "form": form,
        "page_title": "Регистрация",
    })


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Вы вошли в систему.")
                return redirect(request.GET.get("next") or "tours:tour_list")
            messages.error(request, "Неверный логин или пароль.")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {
        "form": form,
        "page_title": "Вход",
    })


def user_logout(request):
    logout(request)
    messages.info(request, "Вы вышли из системы.")
    return redirect("tours:tour_list")


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён.")
            return redirect("users:profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "users/profile.html", {
        "form": form,
        "tours_total": request.user.tours.count(),
        "favorites_total": request.user.favorites.count(),
        "reviews_total": request.user.reviews.count(),
        "page_title": "Профиль",
    })
