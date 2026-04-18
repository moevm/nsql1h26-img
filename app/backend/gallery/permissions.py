from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True

        # not AnonymousUser
        if not bool(request.user and request.user.is_authenticated):
            return False

        # permissions
        return obj.author == request.user or request.user.is_staff
