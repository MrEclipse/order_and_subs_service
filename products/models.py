from django.db import models
from django.db.models import F


class Order(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    subscription = models.ForeignKey('subscriptions.UserSubscription', on_delete=models.PROTECT)
    added_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    count = models.PositiveIntegerField(null=False, default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return 'Заказ ' + str(self.id)


class Product(models.Model):
    name = models.CharField(max_length=255)
    base_price = models.IntegerField()

    def __str__(self):
        return self.name

# Create your models here.
