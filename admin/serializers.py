from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from admin.models import Notary


class NotarySerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)

    class Meta:
        model = Notary
        fields = "__all__"
