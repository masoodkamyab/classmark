from django.core.exceptions import ValidationError
from django.db import transaction

from courses.models import Enrollment

from .models import (
    SESSION_SECTION_COUNT,
    AttendanceRecord,
    AttendanceStatus,
    ClassSession,
    SessionSection,
)


def _validate_status(status):
    if status not in AttendanceStatus.values:
        raise ValidationError({"status": "Select a valid attendance status."})


def _validate_enrollment(*, student, course):
    if (
        not getattr(student, "pk", None)
        or not getattr(course, "pk", None)
        or not Enrollment.objects.filter(
            student=student,
            course=course,
            is_active=True,
        ).exists()
    ):
        raise ValidationError(
            {"student": "Student must be actively enrolled in the course."}
        )


def _validate_session(*, course, session):
    if (
        not getattr(course, "pk", None)
        or not getattr(session, "pk", None)
        or not ClassSession.objects.filter(pk=session.pk, course=course).exists()
    ):
        raise ValidationError(
            {"session": "Session must belong to the selected course."}
        )


def _validate_section(*, session, section):
    if (
        not getattr(session, "pk", None)
        or not getattr(section, "pk", None)
        or not SessionSection.objects.filter(pk=section.pk, session=session).exists()
    ):
        raise ValidationError(
            {"section": "Section must belong to the selected session."}
        )


def _get_session_sections(session):
    sections = list(session.sections.order_by("section_number"))
    if len(sections) != SESSION_SECTION_COUNT:
        raise ValidationError(
            {"session": f"Session must have exactly {SESSION_SECTION_COUNT} sections."}
        )
    return sections


def _mark_attendance(
    *,
    student,
    course,
    session,
    section,
    status,
    recorded_by,
    recorded_method,
    note,
):
    record, _ = AttendanceRecord.objects.update_or_create(
        student=student,
        section=section,
        defaults={
            "course": course,
            "session": session,
            "status": status,
            "recorded_by": recorded_by,
            "recorded_method": recorded_method,
            "note": note,
        },
    )
    return record


def mark_student_for_section(
    *,
    student,
    course,
    session,
    section,
    status,
    recorded_by=None,
    note="",
):
    """Create or update one student's manual attendance for one section."""
    _validate_status(status)
    _validate_enrollment(student=student, course=course)
    _validate_session(course=course, session=session)
    _validate_section(session=session, section=section)

    return _mark_attendance(
        student=student,
        course=course,
        session=session,
        section=section,
        status=status,
        recorded_by=recorded_by,
        recorded_method=AttendanceRecord.RecordedMethod.MANUAL,
        note=note,
    )


@transaction.atomic
def mark_student_for_session(
    *,
    student,
    course,
    session,
    status,
    recorded_by=None,
    note="",
):
    """Create or update one student's manual attendance for all three sections."""
    _validate_status(status)
    _validate_enrollment(student=student, course=course)
    _validate_session(course=course, session=session)
    sections = _get_session_sections(session)

    return [
        _mark_attendance(
            student=student,
            course=course,
            session=session,
            section=section,
            status=status,
            recorded_by=recorded_by,
            recorded_method=AttendanceRecord.RecordedMethod.MANUAL,
            note=note,
        )
        for section in sections
    ]


@transaction.atomic
def bulk_mark_missing_students_absent(*, course, session, recorded_by=None):
    """Mark missing records absent for actively enrolled students."""
    _validate_session(course=course, session=session)
    sections = _get_session_sections(session)
    enrollments = Enrollment.objects.filter(course=course, is_active=True).select_related(
        "student"
    )
    created_records = []

    for enrollment in enrollments:
        for section in sections:
            record, created = AttendanceRecord.objects.get_or_create(
                student=enrollment.student,
                section=section,
                defaults={
                    "course": course,
                    "session": session,
                    "status": AttendanceRecord.Status.ABSENT,
                    "recorded_by": recorded_by,
                    "recorded_method": AttendanceRecord.RecordedMethod.SYSTEM,
                },
            )
            if created:
                created_records.append(record)

    return created_records


@transaction.atomic
def change_attendance_record_manually(
    *,
    record,
    status,
    recorded_by=None,
    note=None,
):
    """Safely change an existing attendance record as a manual correction."""
    _validate_status(status)

    if not record.pk:
        raise ValidationError({"record": "Attendance record must already exist."})

    try:
        record = AttendanceRecord.objects.select_for_update().get(pk=record.pk)
    except AttendanceRecord.DoesNotExist as exc:
        raise ValidationError(
            {"record": "Attendance record must already exist."}
        ) from exc

    _validate_enrollment(student=record.student, course=record.course)
    _validate_session(course=record.course, session=record.session)
    _validate_section(session=record.session, section=record.section)

    record.status = status
    record.recorded_by = recorded_by
    record.recorded_method = AttendanceRecord.RecordedMethod.MANUAL
    if note is not None:
        record.note = note

    record.full_clean()
    record.save(
        update_fields=("status", "recorded_by", "recorded_method", "note")
    )
    return record
