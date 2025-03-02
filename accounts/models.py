from django.contrib.auth.models import AbstractUser, BaseUserManager,PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
import uuid
from cloudinary.models import CloudinaryField  

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not email.endswith(".edu"):
            raise ValidationError("Only .edu emails are allowed.")
            
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)  # ✅ Automatically verify superusers
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser, PermissionsMixin):
    username = None  # Remove username
    email = models.EmailField(unique=True)  # Use email as primary identifier
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)  # Track verification

    verification_token = models.UUIDField(default=uuid.uuid4, unique=True)  # Unique token for verification
    objects = CustomUserManager()  # Set custom manager

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions_set",
        blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = CloudinaryField(upload_to='profile_pics/', blank=True, null=True)
    rating = models.FloatField(default=0.0)  # Default rating starts at 0

    def __str__(self):
        return f"{self.user.email}'s Profile"
