from django.contrib import admin

from .models import AttendanceRecord, ClassSession, SessionSection


class SessionSectionInline(admin.TabularInline):
    model = SessionSection
    extra = 0
    can_delete = False
    readonly_fields = ("section_number", "duration_minutes", "counted_hours")


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ("course", "date", "start_time", "end_time", "status")
    list_filter = ("status", "date")
    search_fields = ("course__code", "course__title")
    list_select_related = ("course",)
    inlines = (SessionSectionInline,)


@admin.register(SessionSection)
class SessionSectionAdmin(admin.ModelAdmin):
    list_display = (
        "session",
        "section_number",
        "duration_minutes",
        "counted_hours",
    )
    list_filter = ("section_number",)
    search_fields = ("session__course__code", "session__course__title")
    list_select_related = ("session", "session__course")
    readonly_fields = ("session", "section_number", "duration_minutes", "counted_hours")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "course",
        "session",
        "section",
        "status",
        "recorded_method",
        "recorded_by",
        "recorded_at",
    )
    list_filter = ("status", "recorded_method", "course")
    search_fields = (
        "student__username",
        "student__student_code",
        "course__code",
        "course__title",
    )
    list_select_related = (
        "student",
        "course",
        "session",
        "section",
        "recorded_by",
    )
    readonly_fields = ("recorded_at",)
