from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission
from question_app.models import Questionnaire


class IsQuestionnaireOwner(BasePermission):
    def has_permission(self, request, view):
        uuid = view.kwargs.get('questionnaire_uuid')
        return request.user == get_object_or_404(Questionnaire, uuid=uuid).owner or request.user.is_staff
