from rest_framework.permissions import BasePermission


class IsQuestionnaireOwner(BasePermission):
    def has_permission(self, request, view):
        uuid = view.kwargs.get('questionnaire_uuid')
        user = request.user
        return user.questionnaires.filter(uuid=uuid).exists() or user.is_staff
