from django.db import models
from studyroom.models import StudySession
from uploads.models import Upload

class Quiz(models.Model):
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name='quizzes')
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE) # Which book was active?
    
    topic_title = models.CharField(max_length=255) # The topic identified from chat
    questions_data = models.JSONField() # Stores: [{"q": "", "options": {}, "answer": ""}]
    
    score = models.IntegerField(null=True, blank=True)
    total_questions = models.IntegerField(default=5)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz: {self.topic_title} ({self.session.subject.name})"