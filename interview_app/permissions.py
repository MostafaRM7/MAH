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
