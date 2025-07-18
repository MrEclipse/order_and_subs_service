import calendar

from django.utils import timezone

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db import models


class Tariff(models.Model):
    name = models.CharField(max_length=20, unique=True)
    rate = models.FloatField()

    def __str__(self):
        return self.name


def default_end():
    now = timezone.now()
    year = now.year + (now.month // 12)
    month = now.month % 12 + 1
    last_day_next_month = calendar.monthrange(year, month)[1]
    day = min(now.day, last_day_next_month)

    return now.replace(year=year, month=month, day=day)


class UserSubscription(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='subscriptions')
    tariff = models.ForeignKey('Tariff', on_delete=models.CASCADE)
    begin = models.DateTimeField(auto_now=True)
    end = models.DateTimeField(default=default_end)

    class Meta:
        # Обычно сортируют либо по началу, либо, как в моем случае
        # в мидлварине, сразу по обоим параметрам
        indexes = [
            models.Index(fields=['begin', 'end'], name='data_subs_index')
        ]

# Create your models here.
