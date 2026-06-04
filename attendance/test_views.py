from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from courses.models import Course, Enrollment

from .models import AttendanceRecord, ClassSession


class TeacherSessionDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.teacher = user_model.objects.create_user(
            username="teacher",
            role=user_model.Role.TEACHER,
        )
        cls.other_teacher = user_model.objects.create_user(
            username="other-teacher",
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
        Enrollment.objects.create(course=cls.course, student=cls.student)
        cls.session = ClassSession.objects.create(
            course=cls.course,
            date=date(2026, 9, 1),
            start_time=time(9, 0),
        )
        first_section = cls.session.sections.get(section_number=1)
        AttendanceRecord.objects.create(
            student=cls.student,
            course=cls.course,
            session=cls.session,
            section=first_section,
            status=AttendanceRecord.Status.PRESENT,
            recorded_by=cls.teacher,
        )

    def test_anonymous_user_is_redirected_from_session_detail(self):
        url = reverse("attendance:session-detail", args=[self.session.pk])

        response = self.client.get(url)

        self.assertRedirects(
            response,
            f"/accounts/login/?next={url}",
            fetch_redirect_response=False,
        )

    def test_student_cannot_access_session_detail(self):
        self.client.force_login(self.student)

        response = self.client.get(
            reverse("attendance:session-detail", args=[self.session.pk])
        )

        self.assertEqual(response.status_code, 403)

    def test_owner_can_view_session_sections_students_and_statuses(self):
        self.client.force_login(self.teacher)

        response = self.client.get(
            reverse("attendance:session-detail", args=[self.session.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2026-09-01")
        self.assertContains(response, "Section 1")
        self.assertContains(response, "Section 2")
        self.assertContains(response, "Section 3")
        self.assertContains(response, self.student.username)
        self.assertContains(response, "Present")
        self.assertContains(response, "Not recorded", count=2)

    def test_other_teacher_cannot_view_session_detail(self):
        self.client.force_login(self.other_teacher)

        response = self.client.get(
            reverse("attendance:session-detail", args=[self.session.pk])
        )

        self.assertEqual(response.status_code, 404)
