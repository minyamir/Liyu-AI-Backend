from django.db import models
from studyroom.models import StudySession
from uploads.models import Upload

class Summary(models.Model):
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name='summaries')
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE) # The book being summarized
    
    topic_title = models.CharField(max_length=255) # e.g., "The Water Cycle"
    content = models.TextField() # The main summary text (Markdown)
    
    # We use a JSONField to store key terms like: [{"term": "Evaporation", "definition": "..."}]
    key_terms = models.JSONField(default=list, blank=True) 
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Summary: {self.topic_title} ({self.session.subject.name})"