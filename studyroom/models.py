from django.db import models
from users.models import User
from subjects.models import Subject

class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    grade_level = models.CharField(max_length=10)
    study_field = models.CharField(max_length=50, null=True, blank=True)
    language = models.CharField(max_length=5, default="en")

    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_tutor_context(self):
        """Packages session data for the Gemini Prompt Builder."""
        return {
            "user_name": self.user.name,
            "subject": self.subject.name,
            "grade": self.grade_level,
            "field": self.study_field or "General",
            "language": "Amharic and English" if self.language == "am" else "English"
        }
        
    def __str__(self):
        return f"{self.user.email} - {self.subject.name}"