from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class Course(models.Model):
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses_taught",
        limit_choices_to={"role": "TEACHER"},
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__gte=F("start_date")),
                name="course_end_date_on_or_after_start_date",
            ),
        ]

    def clean(self):
        super().clean()

        if self.teacher_id and self.teacher.role != self.teacher.Role.TEACHER:
            raise ValidationError(
                {"teacher": "Only users with the teacher role can own a course."}
            )

        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError(
                {"end_date": "End date must be on or after the start date."}
            )

    def __str__(self):
        return f"{self.code} - {self.title}"


class Enrollment(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_enrollments",
        limit_choices_to={"role": "STUDENT"},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("course", "student"),
                name="unique_course_student_enrollment",
            ),
        ]

    def clean(self):
        super().clean()

        if self.student_id and self.student.role != self.student.Role.STUDENT:
            raise ValidationError(
                {"student": "Only users with the student role can be enrolled."}
            )

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"
