from django.urls import path

from . import views

app_name = "attendance"

urlpatterns = [
    path("sessions/<int:session_id>/", views.session_detail, name="session-detail"),
]
