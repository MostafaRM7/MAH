from django.urls import path, include
from rest_framework_nested import routers

from wallet_app.views import WalletViewSet, IncreaseBalanceAPIView, PaymentResultAPIView

router = routers.DefaultRouter()
router.register('wallet', WalletViewSet, basename='wallet')

# wallet_router = routers.NestedDefaultRouter(router, 'wallet', lookup='wallet')
# wallet_router.register('transactions', TransactionViewSet, basename='transactions')


urlpatterns = [
    path('', include(router.urls)),
    path('increase-balance/', IncreaseBalanceAPIView.as_view(), name='increase-balance'),
    path('payment_result/', PaymentResultAPIView.as_view(), name='payment-result')
    # path('', include(wallet_router.urls)),
]
