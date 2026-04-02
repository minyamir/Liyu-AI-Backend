from django.db import models
from studyroom.models import StudySession

class Upload(models.Model):
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name='uploads')
    file = models.FileField(upload_to='UserPDF/') 
    file_type = models.CharField(max_length=20, blank=True)
    extracted_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_valid_for_subject = models.BooleanField(default=False)
    validation_feedback = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.file:
            if self.file.name.endswith('.pdf'):
                self.file_type = 'pdf'
            else:
                self.file_type = 'unknown'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Upload {self.id} - Session {self.session.id}"
