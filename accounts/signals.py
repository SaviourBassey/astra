from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import AdditionalUserInfo

@receiver(post_save, sender=User)
def create_additionaluserinfo(sender, instance, created, **kwargs):
    if created:
        AdditionalUserInfo.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_additionaluserinfo(sender, instance, **kwargs):
    instance.additionaluserinfo.save()
