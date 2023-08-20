from dj_rest_auth.registration.views import RegisterView
from django.db.models import Count
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins, status, serializers
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from builder.models import *
from client.models import Chat
from users.models import CustomUser, Contact
from users.serializers import ProfileSerializer, ContactSerializer


@extend_schema(tags=["Profile"])
class ProfileViewSet(
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ProfileSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', "put", 'patch', 'delete', 'head', 'options']

    def destroy(self, request, *args, **kwargs):
        user = CustomUser.objects.get(pk=kwargs['pk'])
        chats = Chat.objects.annotate(Count('users'))
        for chat in chats:
            if user in chat.users.all() and chat.users__count <= 1:
                chat.delete()
        user.delete()
        return Response('Профиль успешно удалён', status.HTTP_200_OK)

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

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response({
            "count": self.queryset.count(),
            "data": serializer.data,
        })

    class ContactViewSet(viewsets.ModelViewSet):
        serializer_class = ContactSerializer
        queryset = Contact.objects.all()

        http_method_names = ['get', 'patch']


class CustomRegisterView(RegisterView):
    def get_response_data(self, user):
        # Add your custom logic here after registration
        # You can access the newly registered user using the 'user' argument

        # For example, you can create an additional profile for the user
        Contact.objects.create(user=user).save()
        if user.is_builder:
            gallery = Gallery.objects.create()
            doc_kit = DocKit.objects.create()
            obj = Complex.objects.create(builder=user, gallery=gallery, doc_kit=doc_kit)
            Benefit.objects.create(complex_id=obj.id).save()

        # You can also perform other operations like sending an email, creating related objects, etc.

        # Call the parent method to get the default response data
        data = super().get_response_data(user)
        return data
