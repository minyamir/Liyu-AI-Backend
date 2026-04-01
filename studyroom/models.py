from django.db import models
from users.models import User
from subjects.models import Subject

class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    grade_level = models.CharField(max_length=10)
    language = models.CharField(max_length=5, default="en")

    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.subject.name}"