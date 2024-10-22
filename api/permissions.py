from rest_framework import permissions


class AdvertisementPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous and request.method not in permissions.SAFE_METHODS:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ['DELETE', 'PUT', 'PATCH']:
            return obj.creator == request.user
        if request.user.is_staff:
            return True
        return True