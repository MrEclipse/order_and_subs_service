from rest_framework import serializers
from subscriptions.models import Tariff, UserSubscription
from users.serializers import UserSerializer


class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = '__all__'


class UserSubscriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserSubscription
        fields = '__all__'

        read_only_fields = ('begin', 'end')
