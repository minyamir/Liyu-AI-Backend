from django.db import models
from django.conf import settings

class UserProgress(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Points/XP system (Gamification)
    total_xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    
    # Streak logic
    current_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(auto_now=True)
    
    # Mastery Tracking (JSON is flexible for different subjects)
    # Example: {"Biology": 85, "Math": 40}
    subject_mastery = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user.username} - Level {self.level}"