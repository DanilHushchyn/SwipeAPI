from rest_framework import permissions

from client.models import Promotion


class HasComplex(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        return request.user.announcements.filter(pk=obj.pk).exists()


class IsMyApartment(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.apartments.filter(pk=obj.pk).exists()

