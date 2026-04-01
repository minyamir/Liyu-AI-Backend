from django.db import models
from studyroom.models import StudySession

class ChatMessage(models.Model):
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE)
    sender = models.CharField(max_length=10)  # "user" or "ai"
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.message[:30]}"
    