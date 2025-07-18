from rest_framework.routers import DefaultRouter
from subscriptions.views import UserSubscriptionViewSet, GetTariffList

router = DefaultRouter()
router.register('tariffs', GetTariffList, basename='tariffs')
router.register('subs', UserSubscriptionViewSet, basename='subscriptions')

urlpatterns = router.urls
