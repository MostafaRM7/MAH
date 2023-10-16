from rest_framework.permissions import BasePermission


class IsQuestionnaireOwner(BasePermission):
    def has_permission(self, request, view):
        uuid = view.kwargs.get('questionnaire_uuid')
        user = request.user
        if user.is_authenticated:
            profile = request.user.profile
            return profile.questionnaires.filter(uuid=uuid).exists() or user.is_staff
