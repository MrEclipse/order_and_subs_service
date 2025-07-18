from django.shortcuts import render
from subscriptions.models import Tariff, UserSubscription
from rest_framework import mixins, viewsets, permissions
from subscriptions.serializers import TariffSerializer, UserSubscriptionSerializer


class GetTariffList(viewsets.ReadOnlyModelViewSet):
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # возвращаем только подписки, принадлежащие текущему юзеру
        return UserSubscription.objects.filter(user=self.request.user).select_related('user', 'tariff')
        # решаю n+1 проблему
