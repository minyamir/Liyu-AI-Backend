from django.db import models

class Subject(models.Model):
    GRADE_CHOICES = [
        ("7", "Grade 7"),
        ("8", "Grade 8"),
        ("9", "Grade 9"),
        ("10", "Grade 10"),
        ("11", "Grade 11"),
        ("12", "Grade 12"),
        ("uni", "University"),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)  # Science, Language, etc.
    grade_level = models.CharField(max_length=10, choices=GRADE_CHOICES)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (Grade {self.grade_level})"