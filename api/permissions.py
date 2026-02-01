from rest_framework.permissions import BasePermission


class IsRecruiter(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "RECRUITER"


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"
