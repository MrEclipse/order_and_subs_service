from django.http import JsonResponse
from django.urls import resolve
from subscriptions.models import UserSubscription
from django.utils import timezone


class SubscriptionCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1) Пропускаем анонимов
        if not request.user.is_authenticated:
            return self.get_response(request)

        resolver = resolve(request.path_info)
        view_func = resolver.func

        view_cls = getattr(view_func, 'cls', None)

        if view_cls and getattr(view_cls, 'requires_active_subscription', False):
            now = timezone.now()
            has_active = request.user.subscriptions.filter(
                begin__lte=now,
                end__gte=now
            ).exists()
            if not has_active:
                return JsonResponse(
                    {'detail': 'Для доступа нужна активная подписка.'},
                    status=402
                )

        return self.get_response(request)
