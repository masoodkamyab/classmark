from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.course_list, name="course-list"),
    path("<int:course_id>/", views.course_detail, name="course-detail"),
    path(
        "<int:course_id>/sessions/create/",
        views.session_create,
        name="session-create",
    ),
]
