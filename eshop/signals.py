from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, User, Client


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Client.objects.create(user=instance)
