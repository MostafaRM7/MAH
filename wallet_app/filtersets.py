import django_filters

from wallet_app.models import Wallet


class WalletFilterSet(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='transactions__created_at', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='transactions__created_at', lookup_expr='lte')

    class Meta:
        model = Wallet
        fields = ['transactions__created_at']
