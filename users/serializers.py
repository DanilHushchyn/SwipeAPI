from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth import get_user_model, models
from drf_extra_fields.fields import Base64ImageField
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from admin.utils import get_timestamp_path
from users.models import CustomUser, Contact


class AuthLoginSerializer(LoginSerializer):
    username = None


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)
    is_builder = serializers.BooleanField(required=True)

    def custom_signup(self, request, user):
        user.is_builder = self.validated_data.get('is_builder', user.is_builder)
        user.save(update_fields=['is_builder'])

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'is_builder': self.validated_data.get('is_builder', '')
        }


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'phone', 'email']
        read_only_fields = ['id']


class ProfileSerializer(serializers.ModelSerializer):
    agent_contacts = ContactSerializer()
    avatar = Base64ImageField(required=False)

    def update(self, instance, validated_data):
        # Add your custom logic here for updating the instance
        # For example, you can update specific fields of the instance based on the validated_data
        if 'agent_contacts' in validated_data:
            contact = Contact.objects.get(user=instance)
            contact.email = validated_data['agent_contacts'].get('email', contact.email)
            contact.phone = validated_data['agent_contacts'].get('phone', contact.phone)
            contact.first_name = validated_data['agent_contacts'].get('first_name', contact.first_name)
            contact.last_name = validated_data['agent_contacts'].get('last_name', contact.last_name)
            contact.save()
        # You can also perform any additional custom operations
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.notification_type = validated_data.get('notification_type', instance.notification_type)
        instance.redirect_notifications_to_agent = validated_data.get('redirect_notifications_to_agent',
                                                                      instance.redirect_notifications_to_agent)
        instance.save()

        return instance

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'first_name',
            'last_name',
            'phone',
            'email',
            'avatar',
            'is_active',
            'is_staff',
            'last_login',
            'date_joined',
            'notification_type',
            'agent_contacts',
            'redirect_notifications_to_agent',
        ]
