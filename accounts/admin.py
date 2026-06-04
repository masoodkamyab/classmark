from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "student_code",
        "is_staff",
        "is_active",
    )
    list_filter = UserAdmin.list_filter + ("role",)
    search_fields = UserAdmin.search_fields + ("student_code",)
    fieldsets = UserAdmin.fieldsets + (
        (
            "ClassPulse",
            {"fields": ("role", "student_code", "phone_number")},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "ClassPulse",
            {"fields": ("role", "student_code", "phone_number")},
        ),
    )
