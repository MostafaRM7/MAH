from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission, SAFE_METHODS

from interview_app.models import Interview


class InterviewOwnerOrInterviewerReadOnly(BasePermission):
    def has_permission(self, request, view):
        uuid = view.kwargs.get('uuid')
        if request.user.is_authenticated:
            if uuid:
                if request.user.profile.interviews.filter(uuid=uuid).exists() or request.user.is_staff:
                    return True
                else:
                    if request.method in SAFE_METHODS:
                        return request.user.role in ['ie', 'i']
            else:
                return request.user.role in ['ie', 'e'] or request.user.is_staff


class InterviewOwnerOrInterviewerAddAnswer(BasePermission):
    def has_permission(self, request, view):
        is_detail = view.kwargs.get('pk')
        interview_uuid = view.kwargs.get('interview_uuid')
        if request.user.is_authenticated:
            if is_detail:
                answer_set = view.get_object()
                if answer_set.questionnaire.owner == request.user or request.user.is_staff:
                    return True
                else:
                    if answer_set.questionnaire.interviewers.filter(id=request.user.id).exists():
                        return True
            else:
                interview = get_object_or_404(Interview, uuid=interview_uuid)
                return interview.owner == request.user or request.user.is_staff or interview.interviewers.filter(
                    request.user.id).exists()


class IsQuestionOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        uuid = view.kwargs.get('interview_uuid')
        if request.user.is_authenticated:
            return request.user.profile.questionnaires.filter(uuid=uuid).exists() or request.user.is_staff


class ChangePlacementForOwnerOrStaff(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            uuid = view.kwargs.get('interview_uuid')
            if request.user.is_authenticated:
                return request.user.profile.questionnaires.filter(uuid=uuid).exists() or request.user.is_staff
        return False


class IsInterviewer(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role in ['ie', 'i']