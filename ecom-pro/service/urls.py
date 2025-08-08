from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceCategoryViewSet, ServiceViewSet, SubscriptionViewSet,
    AppointmentViewSet, SupportTicketViewSet, ServiceReviewViewSet
)

router = DefaultRouter()
router.register(r'categories', ServiceCategoryViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'tickets', SupportTicketViewSet, basename='ticket')
router.register(r'reviews', ServiceReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]