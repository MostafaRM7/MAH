import django_filters
from django.db.models import Q

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
    INTERVIEWER_ROLE_REQUEST_STATUS_CHOICES = (
        ('a', 'قبول شده'),
        ('r', 'رد شده'),
        ('p', 'نیاز به تایید'),
        ('n', 'بدون در خواست')
    )
    role = django_filters.ChoiceFilter(field_name='role', lookup_expr='exact', choices=Profile.ROLE_CHOICES,
                                       method='filter_role')
    is_admin = django_filters.BooleanFilter(field_name='is_staff', lookup_expr='exact')
    interview_name = django_filters.CharFilter(field_name='interviews_name', lookup_expr='exact',
                                               method='filter_by_interview_name')
    interviewer_role_request_status = django_filters.ChoiceFilter(field_name='interviewer_role_request_status',
                                                                  lookup_expr='exact',
                                                                  choices=INTERVIEWER_ROLE_REQUEST_STATUS_CHOICES,
                                                                  method='filter_interviewer_role_request_status')

    def filter_interviewer_role_request_status(self, queryset, name, value):
        if value == 'a':
            return queryset.filter(ask_for_interview_role=False, is_interview_role_accepted=True,
                                   role__in=['i', 'ie'])
        elif value == 'r':
            return queryset.filter(ask_for_interview_role=False, is_interview_role_accepted=False, role__in=['e', 'n'])
        elif value == 'p':
            return queryset.filter(ask_for_interview_role=True, is_interview_role_accepted=False, role__in=['e', 'n'])
        elif value == 'n':
            return queryset.filter(ask_for_interview_role=False, is_interview_role_accepted=None, role__in=['e', 'n'])
        else:
            return queryset

    def filter_by_interview_name(self, queryset, name, value):
        return queryset.filter(interviews__name__icontains=value)

    def filter_role(self, queryset, name, value):
        return queryset.filter(role=value)

    class Meta:
        model = Profile
        fields = ['role', 'is_admin', 'interview_name', 'interviewer_role_request_status']
