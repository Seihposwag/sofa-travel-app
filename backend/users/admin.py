"""Настройка админ-панели для приложения users."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "display_name", "role", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Профиль", {"fields": ("bio", "avatar", "phone")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Профиль", {"fields": ("email",)}),
    )
