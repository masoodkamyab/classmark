from django import forms
from django.core.exceptions import ValidationError

from attendance.models import ClassSession


class ClassSessionForm(forms.ModelForm):
    class Meta:
        model = ClassSession
        fields = ("date", "start_time", "end_time")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, course, **kwargs):
        super().__init__(*args, **kwargs)
        self.course = course

    def clean_date(self):
        session_date = self.cleaned_data["date"]
        if ClassSession.objects.filter(
            course=self.course,
            date=session_date,
        ).exists():
            raise ValidationError("A session already exists for this course and date.")
        return session_date

    def save(self, commit=True):
        session = super().save(commit=False)
        session.course = self.course
        if commit:
            session.save()
        return session
