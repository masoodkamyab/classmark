from datetime import date, time
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from courses.models import Course, Enrollment

from .models import AttendanceRecord, ClassSession
from .services import (
    bulk_mark_missing_students_absent,
    change_attendance_record_manually,
    mark_student_for_section,
    mark_student_for_session,
)


class AttendanceServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.teacher = user_model.objects.create_user(
            username="teacher",
            role=user_model.Role.TEACHER,
        )
        cls.student = user_model.objects.create_user(
            username="student",
            role=user_model.Role.STUDENT,
            student_code="STU-001",
        )
        cls.second_student = user_model.objects.create_user(
            username="second-student",
            role=user_model.Role.STUDENT,
            student_code="STU-002",
        )
        cls.unenrolled_student = user_model.objects.create_user(
            username="unenrolled-student",
            role=user_model.Role.STUDENT,
            student_code="STU-003",
        )
        cls.course = Course.objects.create(
            title="Introduction to Programming",
            code="CS-101",
            teacher=cls.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 15),
        )
        cls.other_course = Course.objects.create(
            title="Data Structures",
            code="CS-102",
            teacher=cls.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 15),
        )
        Enrollment.objects.create(course=cls.course, student=cls.student)
        Enrollment.objects.create(course=cls.course, student=cls.second_student)
        cls.session = ClassSession.objects.create(
            course=cls.course,
            date=date(2026, 9, 1),
            start_time=time(9, 0),
        )
        cls.other_session = ClassSession.objects.create(
            course=cls.other_course,
            date=date(2026, 9, 1),
            start_time=time(13, 0),
        )
        cls.section = cls.session.sections.get(section_number=1)
        cls.other_section = cls.other_session.sections.get(section_number=1)

    def test_mark_student_for_section_creates_manual_record(self):
        record = mark_student_for_section(
            student=self.student,
            course=self.course,
            session=self.session,
            section=self.section,
            status=AttendanceRecord.Status.PRESENT,
            recorded_by=self.teacher,
            note="Marked during roll call.",
        )

        self.assertEqual(record.status, AttendanceRecord.Status.PRESENT)
        self.assertEqual(record.recorded_by, self.teacher)
        self.assertEqual(record.recorded_method, AttendanceRecord.RecordedMethod.MANUAL)
        self.assertEqual(record.note, "Marked during roll call.")

    def test_mark_student_for_section_updates_existing_record(self):
        existing_record = AttendanceRecord.objects.create(
            student=self.student,
            course=self.course,
            session=self.session,
            section=self.section,
            status=AttendanceRecord.Status.ABSENT,
            recorded_method=AttendanceRecord.RecordedMethod.SYSTEM,
        )

        record = mark_student_for_section(
            student=self.student,
            course=self.course,
            session=self.session,
            section=self.section,
            status=AttendanceRecord.Status.LATE,
            recorded_by=self.teacher,
        )

        self.assertEqual(record.pk, existing_record.pk)
        self.assertEqual(AttendanceRecord.objects.count(), 1)
        self.assertEqual(record.status, AttendanceRecord.Status.LATE)
        self.assertEqual(record.recorded_method, AttendanceRecord.RecordedMethod.MANUAL)

    def test_mark_student_for_section_validates_required_relationships_and_status(self):
        cases = (
            (
                {"student": self.unenrolled_student},
                "student",
            ),
            (
                {
                    "session": self.other_session,
                    "section": self.other_section,
                },
                "session",
            ),
            (
                {"section": self.other_section},
                "section",
            ),
            (
                {"status": "INVALID"},
                "status",
            ),
        )

        for overrides, error_field in cases:
            values = {
                "student": self.student,
                "course": self.course,
                "session": self.session,
                "section": self.section,
                "status": AttendanceRecord.Status.PRESENT,
                "recorded_by": self.teacher,
            }
            values.update(overrides)

            with self.subTest(error_field=error_field):
                with self.assertRaises(ValidationError) as context:
                    mark_student_for_section(**values)

                self.assertIn(error_field, context.exception.message_dict)

    def test_mark_student_for_session_marks_all_three_sections(self):
        records = mark_student_for_session(
            student=self.student,
            course=self.course,
            session=self.session,
            status=AttendanceRecord.Status.LEAVE,
            recorded_by=self.teacher,
            note="Approved leave.",
        )

        self.assertEqual(len(records), 3)
        self.assertEqual(
            list(
                AttendanceRecord.objects.filter(student=self.student).values_list(
                    "section__section_number",
                    "status",
                    "note",
                ).order_by("section__section_number")
            ),
            [
                (1, AttendanceRecord.Status.LEAVE, "Approved leave."),
                (2, AttendanceRecord.Status.LEAVE, "Approved leave."),
                (3, AttendanceRecord.Status.LEAVE, "Approved leave."),
            ],
        )

    def test_mark_student_for_session_is_atomic(self):
        original_update_or_create = AttendanceRecord.objects.update_or_create
        call_count = 0

        def fail_after_first_record(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise RuntimeError("Attendance write failed.")
            return original_update_or_create(*args, **kwargs)

        with patch.object(
            AttendanceRecord.objects,
            "update_or_create",
            side_effect=fail_after_first_record,
        ):
            with self.assertRaises(RuntimeError):
                mark_student_for_session(
                    student=self.student,
                    course=self.course,
                    session=self.session,
                    status=AttendanceRecord.Status.PRESENT,
                    recorded_by=self.teacher,
                )

        self.assertFalse(AttendanceRecord.objects.filter(student=self.student).exists())

    def test_bulk_mark_missing_students_absent_preserves_existing_records(self):
        existing_record = AttendanceRecord.objects.create(
            student=self.student,
            course=self.course,
            session=self.session,
            section=self.section,
            status=AttendanceRecord.Status.PRESENT,
            recorded_by=self.teacher,
        )
        Enrollment.objects.create(
            course=self.course,
            student=self.unenrolled_student,
            is_active=False,
        )

        created_records = bulk_mark_missing_students_absent(
            course=self.course,
            session=self.session,
            recorded_by=self.teacher,
        )

        existing_record.refresh_from_db()
        self.assertEqual(existing_record.status, AttendanceRecord.Status.PRESENT)
        self.assertEqual(len(created_records), 5)
        self.assertEqual(
            AttendanceRecord.objects.filter(
                status=AttendanceRecord.Status.ABSENT,
                recorded_method=AttendanceRecord.RecordedMethod.SYSTEM,
            ).count(),
            5,
        )
        self.assertFalse(
            AttendanceRecord.objects.filter(student=self.unenrolled_student).exists()
        )

    def test_bulk_mark_missing_students_absent_validates_session_course(self):
        with self.assertRaises(ValidationError) as context:
            bulk_mark_missing_students_absent(
                course=self.course,
                session=self.other_session,
            )

        self.assertIn("session", context.exception.message_dict)
        self.assertFalse(AttendanceRecord.objects.exists())

    def test_bulk_mark_missing_students_absent_is_atomic(self):
        original_get_or_create = AttendanceRecord.objects.get_or_create
        call_count = 0

        def fail_after_first_record(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise RuntimeError("Attendance write failed.")
            return original_get_or_create(*args, **kwargs)

        with patch.object(
            AttendanceRecord.objects,
            "get_or_create",
            side_effect=fail_after_first_record,
        ):
            with self.assertRaises(RuntimeError):
                bulk_mark_missing_students_absent(
                    course=self.course,
                    session=self.session,
                )

        self.assertFalse(AttendanceRecord.objects.exists())

    def test_change_attendance_record_manually_updates_existing_record(self):
        record = AttendanceRecord.objects.create(
            student=self.student,
            course=self.course,
            session=self.session,
            section=self.section,
            status=AttendanceRecord.Status.ABSENT,
            recorded_method=AttendanceRecord.RecordedMethod.SYSTEM,
            note="Marked when session ended.",
        )

        changed_record = change_attendance_record_manually(
            record=record,
            status=AttendanceRecord.Status.LEAVE,
            recorded_by=self.teacher,
            note="Excuse approved.",
        )

        self.assertEqual(changed_record.pk, record.pk)
        self.assertEqual(changed_record.status, AttendanceRecord.Status.LEAVE)
        self.assertEqual(changed_record.recorded_by, self.teacher)
        self.assertEqual(
            changed_record.recorded_method,
            AttendanceRecord.RecordedMethod.MANUAL,
        )
        self.assertEqual(changed_record.note, "Excuse approved.")

    def test_change_attendance_record_manually_validates_status_and_enrollment(self):
        record = AttendanceRecord.objects.create(
            student=self.student,
            course=self.course,
            session=self.session,
            section=self.section,
            status=AttendanceRecord.Status.PRESENT,
        )

        with self.assertRaises(ValidationError) as context:
            change_attendance_record_manually(record=record, status="INVALID")
        self.assertIn("status", context.exception.message_dict)

        Enrollment.objects.filter(course=self.course, student=self.student).update(
            is_active=False
        )
        with self.assertRaises(ValidationError) as context:
            change_attendance_record_manually(
                record=record,
                status=AttendanceRecord.Status.LATE,
            )
        self.assertIn("student", context.exception.message_dict)
