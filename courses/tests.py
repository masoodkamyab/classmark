from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Course, Enrollment


class CourseModelTests(TestCase):
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

    def make_course(self, **overrides):
        values = {
            "title": "Introduction to Programming",
            "code": "CS-101",
            "teacher": self.teacher,
            "start_date": date(2026, 9, 1),
            "end_date": date(2026, 12, 15),
        }
        values.update(overrides)
        return Course(**values)

    def test_teacher_can_own_course(self):
        course = self.make_course()

        course.full_clean()
        course.save()

        self.assertEqual(course.teacher, self.teacher)
        self.assertTrue(course.is_active)

    def test_non_teacher_cannot_own_course(self):
        course = self.make_course(teacher=self.student)

        with self.assertRaises(ValidationError) as context:
            course.full_clean()

        self.assertIn(
            "Only users with the teacher role can own a course.",
            context.exception.message_dict["teacher"],
        )

    def test_end_date_cannot_be_before_start_date(self):
        course = self.make_course(end_date=date(2026, 8, 31))

        with self.assertRaises(ValidationError) as context:
            course.full_clean()

        self.assertEqual(
            context.exception.message_dict["end_date"],
            ["End date must be on or after the start date."],
        )

    def test_date_order_is_enforced_by_database_constraint(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Course.objects.create(
                title="Invalid Course",
                code="INVALID",
                teacher=self.teacher,
                start_date=date(2026, 9, 1),
                end_date=date(2026, 8, 31),
            )

    def test_string_representation_contains_code_and_title(self):
        course = self.make_course()

        self.assertEqual(str(course), "CS-101 - Introduction to Programming")


class EnrollmentModelTests(TestCase):
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
        cls.course = Course.objects.create(
            title="Introduction to Programming",
            code="CS-101",
            teacher=cls.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 15),
        )

    def test_student_can_be_enrolled_in_course(self):
        enrollment = Enrollment(course=self.course, student=self.student)

        enrollment.full_clean()
        enrollment.save()

        self.assertEqual(enrollment.course, self.course)
        self.assertEqual(enrollment.student, self.student)
        self.assertTrue(enrollment.is_active)

    def test_non_student_cannot_be_enrolled(self):
        enrollment = Enrollment(course=self.course, student=self.teacher)

        with self.assertRaises(ValidationError) as context:
            enrollment.full_clean()

        self.assertIn(
            "Only users with the student role can be enrolled.",
            context.exception.message_dict["student"],
        )

    def test_student_cannot_be_enrolled_twice_in_same_course(self):
        Enrollment.objects.create(course=self.course, student=self.student)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Enrollment.objects.create(course=self.course, student=self.student)

    def test_string_representation_identifies_student_and_course(self):
        enrollment = Enrollment(course=self.course, student=self.student)

        self.assertEqual(
            str(enrollment),
            "student enrolled in CS-101 - Introduction to Programming",
        )
