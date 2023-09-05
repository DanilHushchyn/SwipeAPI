from dj_rest_auth.registration.views import RegisterView
from django.db.models import Count
from drf_psq import Rule, PsqMixin
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins, status, serializers
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from builder.models import *
from client.models import Chat, Subscription
from users.models import CustomUser, Contact
from users.permissions import IsMyProfile
from users.serializers import ProfileSerializer, ContactSerializer
from django.utils import timezone
from dateutil.relativedelta import relativedelta


@extend_schema(tags=["Profile"])
class ProfileViewSet(
    PsqMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ProfileSerializer
    queryset = CustomUser.objects.all()
    http_method_names = ['get', "put", 'patch', 'delete']
    parser_classes = [JSONParser]
    psq_rules = {
        ('list', 'blacklist', 'switch_blacklist'): [
            Rule([IsAdminUser], ProfileSerializer),
        ],
        ('my_profile', 'retrieve', 'destroy', 'update_my_profile'): [
            Rule([IsAuthenticated], ProfileSerializer),
        ]
    }

    def destroy(self, request, *args, **kwargs):
        user = CustomUser.objects.get(pk=kwargs['pk'])
        chats = Chat.objects.annotate(Count('users'))
        for chat in chats:
            if user in chat.users.all() and chat.users__count <= 1:
                chat.delete()
        user.delete()
        return Response('Профиль успешно удалён', status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        active_profiles = self.queryset.filter(is_active=True)
        serializer = self.serializer_class(active_profiles, many=True)
        return Response({
            "count": active_profiles.count(),
            "data": serializer.data,
        })

    @extend_schema(
        methods=["GET"],
        description="Get authenticated user profile",
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="my_profile",
    )
    def my_profile(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)

    @extend_schema(
        methods=["PATCH"],
        description="Update authenticated user profile",
    )
    @action(
        detail=False,
        methods=["patch"],
        url_path="update_my_profile",
    )
    def update_my_profile(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        methods=["GET"],
        description="Get blacklist's profiles",
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="blacklist",
    )
    def blacklist(self, request, *args, **kwargs):
        blocked_profiles = self.queryset.filter(is_active=False)
        serializer = self.serializer_class(blocked_profiles, many=True)
        return Response({
            "count": blocked_profiles.count(),
            "data": serializer.data,
        })

    @extend_schema(request=serializers.Serializer)
    @action(detail=True, methods=["put"], name="switch_blacklist",
            url_path="switch_blacklist",
            )
    def switch_blacklist(self, request, *args, **kwargs):
        user = get_object_or_404(CustomUser, pk=kwargs.get("pk"))
        if not user.is_active:
            user.is_active = True
            user.save()
            return Response('Пользователь удалён из чёрного списка')
        user.is_active = False
        user.save()
        return Response('Пользователь добавлен в чёрный список')


class CustomRegisterView(RegisterView):
    def get_response_data(self, user):
        # Add your custom logic here after registration
        # You can access the newly registered user using the 'user' argument
        # For example, you can create an additional profile for the user
        Contact.objects.create(user=user)
        Subscription.objects.create(client=user, expiration_date=timezone.now() + timezone.timedelta(days=30),
                                    auto_renewal=True)

        # if user.is_builder:
        # gallery = Gallery.objects.create()
        # doc_kit = DocKit.objects.create()
        # obj = Complex.objects.create(builder=user)
        # Benefit.objects.create(complex_id=obj.id).save()

        # You can also perform other operations like sending an email, creating related objects, etc.
        # Call the parent method to get the default response data
        data = super().get_response_data(user)
        return data
