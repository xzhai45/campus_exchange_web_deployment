from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Profile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a profile when a new user registers."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Ensure profile is saved when the user is updated."""
    instance.profile.save()
