import django_filters

from interview_app.models import Interview
from user_app.models import Profile


class InterviewFilterSet(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    approval_status = django_filters.CharFilter(field_name='approval_status', lookup_expr='exact')

    class Meta:
        model = Interview
        fields = ['created_at', 'approval_status']


class ProfileFilterSet(django_filters.FilterSet):
    role = django_filters.CharFilter(field_name='role', lookup_expr='exact')
    is_admin = django_filters.BooleanFilter(field_name='is_staff', lookup_expr='exact')

    class Meta:
        model = Profile
        fields = ['role', 'is_admin']
