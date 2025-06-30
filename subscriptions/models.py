from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db import models

class Tariff(models.Model):
    name = models.CharField(max_length=20, unique=True)
    rate = models.FloatField()

    def __str__(self):
        return self.name

class UserSubscription(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    tariff = models.ForeignKey('Tariff', on_delete=models.CASCADE)

# Create your models here.
