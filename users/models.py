from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=16, unique=True)
    telegram_id = models.CharField(max_length=255, default="", blank=True)

    def __str__(self):
        return self.username
# Create your models here.
