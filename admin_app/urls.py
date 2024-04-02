from django.urls import path, include
from rest_framework import routers
from admin_app.views import InterviewViewSet, ProfileViewSet, PricePackViewSet, TicketViewSet

router = routers.DefaultRouter()
router.register(r'interviews', InterviewViewSet, basename='admin-interviews')
router.register(r'users', ProfileViewSet, basename='admin-users')
router.register(r'price-packs', PricePackViewSet, basename='price-packs')
router.register(r'tickets', TicketViewSet, basename='admin-tickets')

urlpatterns = [
    path('', include(router.urls)),
]
