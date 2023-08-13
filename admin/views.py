from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from admin.models import Notary
from admin.serializers import NotarySerializer


@extend_schema(tags=["Notaries"])
class NotaryViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """

    queryset = Notary.objects.all()
    serializer_class = NotarySerializer
    permission_classes = [IsAuthenticated]
