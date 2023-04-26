from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Questionnaire


class IsQuestionnaireOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        uuid = view.kwargs.get('uuid')
        if uuid:
            if request.method in SAFE_METHODS:
                return True
            else:
                return request.user == Questionnaire.objects.get(uuid=uuid).owner or request.user.is_staff
        else:
            if request.method == 'POST':
                return request.user.is_authenticated or request.user.is_staff
            else:
                return request.user.is_staff


class IsQuestionOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        question_id = view.kwargs.get('id')
        questionnaire = Questionnaire.objects.get(uuid=view.kwargs.get('questionnaire_uuid'))
        if question_id:
            if request.user.is_authenticated:
                return questionnaire in request.user.questionnaires.all() or request.user.is_staff
        else:
            if request.method == 'POST':
                return request.user.is_authenticated
            else:
                if request.user.is_authenticated:
                    return questionnaire in request.user.questionnaires.all() or request.user.is_staff


class AnonPOSTOrOwner(BasePermission):
    def has_permission(self, request, view):
        answer_set_id = view.kwargs.get('id')
        questionnaire = Questionnaire.objects.get(uuid=view.kwargs.get('questionnaire_uuid'))
        if answer_set_id:
            if request.user.is_authenticated:
                return questionnaire in request.user.questionnaires.all() or request.user.is_staff
        else:
            if request.method == 'POST':
                return True
            else:
                if request.user.is_authenticated:
                    return questionnaire in request.user.questionnaires.all() or request.user.is_staff


class IsPageOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        page_id = view.kwargs.get('id')
        questionnaire = Questionnaire.objects.get(uuid=view.kwargs.get('questionnaire_uuid'))
        if page_id:
            if request.user.is_authenticated:
                return questionnaire in request.user.questionnaires.all() or request.user.is_staff
        else:
            if request.method == 'POST':
                return request.user.is_authenticated
            else:
                return questionnaire in request.user.questionnaires.all() or request.user.is_staff
