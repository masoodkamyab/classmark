from django.shortcuts import get_object_or_404, render

from accounts.decorators import teacher_required
from courses.models import Enrollment

from .models import AttendanceRecord, ClassSession


@teacher_required
def session_detail(request, session_id):
    session = get_object_or_404(
        ClassSession.objects.select_related("course"),
        pk=session_id,
        course__teacher=request.user,
    )
    sections = list(session.sections.all())
    enrollments = list(
        Enrollment.objects.filter(course=session.course, is_active=True)
        .select_related("student")
        .order_by("student__username")
    )
    attendance_records = AttendanceRecord.objects.filter(
        session=session,
        student_id__in=[enrollment.student_id for enrollment in enrollments],
    )
    records_by_student_and_section = {
        (record.student_id, record.section_id): record
        for record in attendance_records
    }
    attendance_rows = []
    for enrollment in enrollments:
        statuses = []
        for section in sections:
            record = records_by_student_and_section.get(
                (enrollment.student_id, section.pk)
            )
            statuses.append(record.get_status_display() if record else "Not recorded")
        attendance_rows.append({"student": enrollment.student, "statuses": statuses})

    return render(
        request,
        "attendance/session_detail.html",
        {
            "session": session,
            "sections": sections,
            "attendance_rows": attendance_rows,
        },
    )
