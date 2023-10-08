from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from interview_app.interview_app_serializers.general_serializers import InterviewSerializer
from interview_app.models import Interview


# Create your views here.


class InterviewViewSet(viewsets.ModelViewSet):
    serializer_class = InterviewSerializer
    permission_classes = (AllowAny,)
    lookup_field = 'uuid'
    queryset = Interview.objects.all()

    # def initial(self, request, *args, **kwargs):
    #     if kwargs.get('uuid'):
    #         print(kwargs.get('uuid'))
    #         try:
    #             UUID(kwargs.get('uuid'))
    #         except ValueError:
    #             return Response({"detail": "یافت نشد."}, status.HTTP_404_NOT_FOUND)

        # super(InterviewViewSet, self).initial(request, *args, **kwargs)

    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     if instance.is_active and instance.pub_date <= timezone.now():
    #         if instance.end_date:
    #             if instance.end_date >= timezone.now():
    #                 serializer = self.get_serializer(instance)
    #                 return Response(serializer.data)
    #             else:
    #                 return Response({"detail": "پرسشنامه فعال نیست یا امکان پاسخ دهی به آن وجود ندارد"},
    #                                 status.HTTP_403_FORBIDDEN)
    #         serializer = self.get_serializer(instance)
    #         return Response(serializer.data)
    #     else:
    #         return Response({"detail": "پرسشنامه فعال نیست یا امکان پاسخ دهی به آن وجود ندارد"},
    #                         status.HTTP_403_FORBIDDEN)