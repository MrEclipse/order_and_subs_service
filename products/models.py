from django.db import models
from django.db.models import F

class Order(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    subscription = models.ForeignKey('subscriptions.UserSubscription', on_delete=models.PROTECT)
    added_at = models.DateTimeField(auto_created=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    total_price = F('product__base_price') * F('subscription__tariff__rate')

    def __str__(self):
        return 'Заказ ' + str(self.id)

class Product(models.Model):
    name = models.CharField(max_length=255)
    base_price = models.IntegerField()

    def __str__(self):
        return self.name

# Create your models here.
