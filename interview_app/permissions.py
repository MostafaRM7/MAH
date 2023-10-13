from rest_framework.permissions import BasePermission


class InterviewerOrEmployerOrIsStaff(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            if user.is_staff:
                return True
            else:
                match user.role:
                    # interviewer
                    case 'i':
                        pass
                    # employer
                    case 'e':
                        pass
                    # interviewer and employer
                    case 'ie':
                        pass
                    case _:
                        pass


class IsInterviewOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        uuid = view.kwargs.get('uuid')
        if request.user.is_authenticated:
            if request.user.profile.role in ['i', 'ie', 'e']:
                if uuid:
                    return request.user.profile.questionnaires.filter(uuid=uuid).exists() or request.user.is_staff
                else:
                    if request.method == 'POST':
                        return request.user.is_authenticated
                    else:
                        return request.user.is_staff


class IsQuestionOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        question_id = view.kwargs.get('pk')
        uuid = view.kwargs.get('interview_uuid')
        if request.user.is_authenticated:
            if question_id:
                if request.user.is_authenticated:
                    return request.user.profile.questionnaires.filter(uuid=uuid).exists() or request.user.is_staff
            else:
                if request.user.is_authenticated:
                    return request.user.profile.questionnaires.filter(uuid=uuid).exists() or request.user.is_staff


class ChangePlacementForOwnerOrStaff(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            uuid = view.kwargs.get('interview_uuid')
            if request.user.is_authenticated:
                return request.user.profile.questionnaires.filter(uuid=uuid).exists() or request.user.is_staff
        return False


class AnonPOSTOrOwner(BasePermission):
    def has_permission(self, request, view):
        answer_set_id = view.kwargs.get('pk')
        uuid = view.kwargs.get('interview_uuid')
        if request.user.is_authenticated:
            if answer_set_id:
                if request.user.is_authenticated and request.method != 'POST':
                    return request.user.profile.questionnaires.filter(uuid=uuid).exists() or request.user.is_staff
                else:
                    return True
        else:
            if request.method == 'POST':
                return True
            else:
                if request.user.is_authenticated:
                    return request.user.profile.questionnaires.filter(uuid=uuid).exists() or request.user.is_staff


class IsPageOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        page_id = view.kwargs.get('pk')
        uuid = view.kwargs.get('interview_uuid')
        if page_id:
            if request.user.is_authenticated:
                return request.user.profile.questionnaires.filter(uuid=uuid).exists() or request.user.is_staff
        else:
            if request.method == 'POST':
                return request.user.is_authenticated
            else:
                if request.user.is_authenticated:
                    return request.user.profile.questionnaires.filter(uuid=uuid).exists() or request.user.is_staff
