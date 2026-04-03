from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        # Ensure default values for a regular user
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Set required flags for superuser
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None  # remove username completely

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    GRADE_CHOICES = [
        ("7", "Grade 7"),
        ("8", "Grade 8"),
        ("9", "Grade 9"),
        ("10", "Grade 10"),
        ("11", "Grade 11"),
        ("12", "Grade 12"),
        ("uni", "University"),
    ]

    FIELD_CHOICES = [
        ("social", "Social Sciences"),
        ("natural", "Natural Sciences"),
        ("general", "General"),
    ]

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("am", "Amharic"),
    ]

    grade_level = models.CharField(
        max_length=10,
        choices=GRADE_CHOICES,
        null=True,
        blank=True
    )
    
    study_field = models.CharField(
        max_length=10,
        choices=FIELD_CHOICES,
        null=True,
        blank=True,
        help_text="Required only for grade 11 and 12"
    )

    preferred_language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default="en"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]
    objects = UserManager()

    def __str__(self):
        return self.email