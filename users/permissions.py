from rest_framework import permissions


class IsMyProfile(permissions.BasePermission):
    """
    A custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):

        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user