import django_filters

from question_app.models import AnswerSet


class AnswerSetFilterSet(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='answered_at', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='answered_at', lookup_expr='lte')

    class Meta:
        model = AnswerSet
        fields = ['answered_at']
