from django.db import models
from studyroom.models import StudySession

class Upload(models.Model):
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name='uploads')
    file = models.FileField(upload_to='UserPDF/')
    file_type = models.CharField(max_length=20, blank=True)  # pdf (for now)
    extracted_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Upload {self.id} - Session {self.session.id}"
