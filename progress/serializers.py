from rest_framework import serializers
from .models import UserProgress

class UserProgressSerializer(serializers.ModelSerializer):
    # We can add custom "Method Fields" to calculate things on the fly
    rank_title = serializers.SerializerMethodField()
    next_level_xp = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = UserProgress
        fields = [
            'level', 
            'total_xp', 
            'current_streak', 
            'subject_mastery', 
            'rank_title', 
            'next_level_xp',
            'progress_percentage',
            'last_activity_date'
        ]

    def get_rank_title(self, obj):
        """Returns a 'Cyberpunk' style rank based on level."""
        if obj.level < 5:
            return "Novice Learner"
        elif obj.level < 15:
            return "Scholar"
        elif obj.level < 30:
            return "Cyber-Sage"
        return "Liyu Master"

    def get_next_level_xp(self, obj):
        """Calculates how much XP is needed for the next level (assuming 100 per level)."""
        return (obj.level * 100)

    def get_progress_percentage(self, obj):
        """Calculates 0-100% progress within the current level."""
        current_level_base = (obj.level - 1) * 100
        xp_in_level = obj.total_xp - current_level_base
        return min(max(xp_in_level, 0), 100) # Returns 0-100