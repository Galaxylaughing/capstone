from django.db import models
from django.contrib.auth.models import AbstractUser

from booktracker import helper


# Create your models here.

class User(AbstractUser):
    """Extend functionality of Django's default User model"""

    """hash_id should use the create_hash function and be unique"""                     
    hash_id = models.CharField(max_length=32, default=helper.create_hash, unique=True)


# from: https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

# generates a token for each User upon .save()
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
