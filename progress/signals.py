from django.db.models.signals import post_save
from django.dispatch import receiver
from quiz.models import Quiz
from .models import UserProgress

from django.contrib.auth import get_user_model
User = get_user_model()

@receiver(post_save, sender=User)
def create_user_progress(sender, instance, created, **kwargs):
    if created:
        UserProgress.objects.create(user=instance)

@receiver(post_save, sender=Quiz)
def update_student_progress(sender, instance, created, **kwargs):
    if instance.is_completed:
        # 1. Get or create the progress record
        progress, _ = UserProgress.objects.get_or_create(user=instance.session.user)
        
        # 2. Add XP (e.g., 10 XP per correct answer)
        points_earned = instance.score * 10
        progress.total_xp += points_earned
        
        # 3. Simple Level Up Logic (Every 100 XP)
        progress.level = (progress.total_xp // 100) + 1
        
        # 4. Update Subject Mastery
        subject_name = instance.session.subject.name
        current_mastery = progress.subject_mastery.get(subject_name, 0)
        # Weight the new score into the average
        new_mastery = (current_mastery + (instance.score / instance.total_questions * 100)) / 2
        progress.subject_mastery[subject_name] = round(new_mastery, 1)
        
        progress.save()