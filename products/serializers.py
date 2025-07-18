from rest_framework import serializers
from products.models import Order
from decimal import Decimal

from subscriptions.models import UserSubscription


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['added_at', 'updated_at', 'total_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request', None)
        if request and not request.user.is_anonymous:
            self.fields['subscription'].queryset = UserSubscription.objects.filter(user=request.user)

    def validate_subscription(self, value):
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("Нельзя использовать чужую подписку")
        return value

    @staticmethod
    def _calc_total_price(product, count, subscription):
        return (product.base_price or Decimal('0')) * (subscription.tariff.rate or Decimal('0')) * count

    def create(self, validated_data):
        total_price = self._calc_total_price(validated_data['product'], validated_data['count'], validated_data['subscription'])
        validated_data['total_price'] = total_price
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Если через updated_fields делать и сохранять два раза, то
        # получается два sql запроса. а вот так работает через один
        total_price = self._calc_total_price(validated_data['product'], validated_data['count'], validated_data['subscription'])
        validated_data['total_price'] = total_price
        return super().update(instance, validated_data)

