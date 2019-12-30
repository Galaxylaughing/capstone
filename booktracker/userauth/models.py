from django.db import models
from django.contrib.auth.models import AbstractUser

from booktracker import helper


# Create your models here.

class User(AbstractUser):
    """Extend functionality of Django's default User model"""

    """hash_id should use the create_hash function and be unique"""                     
    hash_id = models.CharField(max_length=32, default=helper.create_hash, unique=True)
