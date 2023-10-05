from django.urls import path, include
from rest_framework_nested import routers

from wallet_app.views import WalletViewSet

router = routers.DefaultRouter()
router.register('wallet', WalletViewSet, basename='wallet')

# wallet_router = routers.NestedDefaultRouter(router, 'wallet', lookup='wallet')
# wallet_router.register('transactions', TransactionViewSet, basename='transactions')


urlpatterns = [
    path('', include(router.urls)),
    # path('', include(wallet_router.urls)),
]
