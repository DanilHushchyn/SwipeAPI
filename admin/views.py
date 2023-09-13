from django.shortcuts import render
from drf_psq import Rule, PsqMixin
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from admin.models import Notary
from admin.serializers import NotarySerializer


@extend_schema(tags=["Notaries"])
class NotaryViewSet(PsqMixin, viewsets.ModelViewSet):
    queryset = Notary.objects.all()
    serializer_class = NotarySerializer
    parser_classes = [MultiPartParser]
    http_method_names = ['get', 'post', 'delete', 'patch']
    psq_rules = {
        ('create', 'partial_update', 'destroy'): [
            Rule([IsAdminUser], NotarySerializer),
        ],
        ('retrieve', 'list'): [
            Rule([IsAuthenticated | IsAdminUser], NotarySerializer),
        ]
    }

    @extend_schema(description='Permissions: IsAuthenticated.\nGet list of notaries.')
    def list(self, request, *args, **kwargs):
        return super().list(request, args, kwargs)

    @extend_schema(description='Permissions: IsAdminUser.\nGet notary by id.')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, args, kwargs)

    @extend_schema(description='Permissions: IsAdminUser.\nCreate new notary.')
    def create(self, request, *args, **kwargs):
        return super().create(request, args, kwargs)

    @extend_schema(description='Permissions: IsAdminUser.\nUpdate notary by id.')
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, args, kwargs)

    @extend_schema(description='Permissions: IsAdminUser.\nDelete notary by id.')
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, args, kwargs)
