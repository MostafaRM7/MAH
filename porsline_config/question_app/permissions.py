from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Questionnaire


class IsQuestionnaireOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        uuid = view.kwargs.get('uuid')
        if uuid:
            return request.user == get_object_or_404(Questionnaire, uuid=uuid) or request.user.is_staff
        else:
            if request.method == 'POST':
                return request.user.is_authenticated
            else:
                return request.user.is_staff


class IsQuestionOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        question_id = view.kwargs.get('id')
        questionnaire = get_object_or_404(Questionnaire, uuid=view.kwargs.get('questionnaire_uuid'))
        if question_id:
            if request.user.is_authenticated:
                return questionnaire in request.user.questionnaires.all() or request.user.is_staff
        else:
            if request.user.is_authenticated:
                return questionnaire in request.user.questionnaires.all() or request.user.is_staff


class ChangePlacementForOwnerOrStaff(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            questionnaire = get_object_or_404(Questionnaire, uuid=view.kwargs.get('questionnaire_uuid'))
            if request.user.is_authenticated:
                return questionnaire in request.user.questionnaires.all() or request.user.is_staff
        return False


class AnonPOSTOrOwner(BasePermission):
    def has_permission(self, request, view):
        answer_set_id = view.kwargs.get('id')
        questionnaire = get_object_or_404(Questionnaire, uuid=view.kwargs.get('questionnaire_uuid'))
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
        questionnaire = get_object_or_404(Questionnaire, uuid=view.kwargs.get('questionnaire_uuid'))
        if page_id:
            if request.user.is_authenticated:
                return questionnaire in request.user.questionnaires.all() or request.user.is_staff
        else:
            if request.method == 'POST':
                return request.user.is_authenticated
            else:
                if request.user.is_authenticated:
                    return questionnaire in request.user.questionnaires.all() or request.user.is_staff
