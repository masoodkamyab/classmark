from django.contrib import admin

from .models import Course, Enrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "title",
        "teacher",
        "start_date",
        "end_date",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("code", "title", "teacher__username")
    list_select_related = ("teacher",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = (
        "student__username",
        "student__student_code",
        "course__code",
        "course__title",
    )
    list_select_related = ("student", "course")
