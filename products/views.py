from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from products.serializers import OrderSerializer

from rest_framework import viewsets
from products.models import Order
from rabbit import new_order_notification


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    requires_active_subscription = True

    def perform_create(self, serializer):
        sub = serializer.validated_data['subscription']
        if sub.user != self.request.user:
            raise PermissionDenied("Нельзя использовать чужую подписку")

        order = serializer.save()
        tg_id = order.subscription.user.telegram_id
        new_order_notification(str(tg_id))

    def get_queryset(self):
        return super().get_queryset().filter(subscription__user=self.request.user).select_related(
            'product', 'subscription__user', 'subscription__tariff')
