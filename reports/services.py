from collections import Counter

from attendance.models import AttendanceRecord, AttendanceStatus
from courses.models import Enrollment


REPORT_STATUSES = (
    AttendanceStatus.PRESENT,
    AttendanceStatus.LATE,
    AttendanceStatus.ABSENT,
    AttendanceStatus.LEAVE,
)


def calculate_attendance_totals(status_counts):
    """Return attendance report totals from per-status section counts."""
    present_sections = status_counts.get(AttendanceStatus.PRESENT, 0)
    late_sections = status_counts.get(AttendanceStatus.LATE, 0)
    absent_sections = status_counts.get(AttendanceStatus.ABSENT, 0)
    leave_sections = status_counts.get(AttendanceStatus.LEAVE, 0)
    late_equivalent_absences = late_sections // 3

    return {
        "present_sections": present_sections,
        "late_sections": late_sections,
        "absent_sections": absent_sections,
        "leave_sections": leave_sections,
        "absence_hours": absent_sections,
        "late_equivalent_absences": late_equivalent_absences,
        "total_absence_equivalent": absent_sections + late_equivalent_absences,
    }


def _empty_status_counts():
    return {status: 0 for status in REPORT_STATUSES}


def _student_summary(*, student, status_counts):
    summary = {"student": student}
    summary.update(calculate_attendance_totals(status_counts))
    return summary


def get_course_report(course):
    """Calculate report totals for each active student in a course."""
    enrollments = list(
        Enrollment.objects.filter(course=course, is_active=True)
        .select_related("student")
        .order_by("student__username")
    )
    student_ids = [enrollment.student_id for enrollment in enrollments]
    counts_by_student = {
        student_id: _empty_status_counts() for student_id in student_ids
    }

    records = (
        AttendanceRecord.objects.filter(course=course, student_id__in=student_ids)
        .values_list("student_id", "status")
        .order_by()
    )
    for student_id, status in records:
        counts_by_student[student_id][status] += 1

    return [
        _student_summary(
            student=enrollment.student,
            status_counts=counts_by_student[enrollment.student_id],
        )
        for enrollment in enrollments
    ]


def get_student_report(course, student):
    """Calculate one student's course report and raw attendance records."""
    records = list(
        AttendanceRecord.objects.filter(course=course, student=student)
        .select_related("session", "section", "recorded_by")
        .order_by(
            "session__date",
            "session__start_time",
            "section__section_number",
        )
    )
    status_counts = Counter(record.status for record in records)

    return {
        "summary": _student_summary(student=student, status_counts=status_counts),
        "records": records,
    }


def get_course_attendance_records(course):
    """Return raw attendance records for a course report export."""
    return (
        AttendanceRecord.objects.filter(course=course)
        .select_related("session", "section", "student")
        .order_by(
            "session__date",
            "session__start_time",
            "section__section_number",
            "student__username",
        )
    )
