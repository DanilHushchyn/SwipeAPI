from rest_framework import permissions

from client.models import Promotion


class IsMyAnnouncement(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.announcements.filter(pk=obj.pk).exists()


class IsMyPromotion(permissions.BasePermission):

    def has_object_permission(self, request, view, obj: Promotion):
        print(obj.announcement.client == request.user)
        return obj.announcement.client == request.user


class IsClient(permissions.BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):

        return bool(request.user.is_authenticated and request.user and ~request.user.is_staff and ~request.user.is_builder)


class IsBuilder(permissions.BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user and ~request.user.is_staff and request.user.is_builder)
