from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import teacher_required

from .forms import ClassSessionForm
from .models import Course


@teacher_required
def course_list(request):
    courses = Course.objects.filter(teacher=request.user).order_by("code", "title")
    return render(request, "courses/course_list.html", {"courses": courses})


@teacher_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id, teacher=request.user)
    enrollments = course.enrollments.filter(is_active=True).select_related("student")
    sessions = course.sessions.order_by("-date", "-start_time")
    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "enrollments": enrollments,
            "sessions": sessions,
        },
    )


@teacher_required
def session_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id, teacher=request.user)
    form = ClassSessionForm(request.POST or None, course=course)

    if request.method == "POST" and form.is_valid():
        session = form.save()
        return redirect("attendance:session-detail", session_id=session.pk)

    return render(
        request,
        "courses/session_form.html",
        {"course": course, "form": form},
    )
