from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from client.serializers import *
from users.models import *


@extend_schema(tags=["Announcements"])
@extend_schema(
    methods=["GET"], description="Get all announcements. Permissions: IsAuthenticated"
)
@extend_schema(methods=["PUT", "PATCH"], description="Update specific announcement.")
@extend_schema(methods=["POST"], description="Create new announcement.")
class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    queryset = Announcement.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)

    # @extend_schema(
    #     methods=["GET"],
    #     description="Get apartments for a specific section in specific complex.",
    # )
    # @action(
    #     detail=False,
    #     methods=["get"],
    #     url_path="sort_by_complex/(?P<complex_id>[^/.]+)",
    # )
    # def sort_by_complex(self, request, complex_id=None):
    #     news = self.queryset.filter(complex_id=complex_id)
    #     serializer = self.serializer_class(news, many=True)
    #     return Response(serializer.data)


@extend_schema(tags=["Subscriptions"])
class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()
    permission_classes = [IsAuthenticated]


@extend_schema(tags=["Promotions"])
class PromotionViewSet(viewsets.ModelViewSet):
    serializer_class = PromotionSerializer
    queryset = Promotion.objects.all()
    permission_classes = [IsAuthenticated]


@extend_schema(tags=["Filters"])
class FilterViewSet(viewsets.ModelViewSet):
    serializer_class = FilterSerializer
    queryset = Filter.objects.all()
    permission_classes = [IsAuthenticated]


@extend_schema(tags=["Chats"])
class ChatViewSet(
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        description="Get all chats for a specific user.",
    )
    def list(self, request):
        user = CustomUser.objects.prefetch_related("chat_set").get(pk=self.request.user.id)
        chats = user.chat_set.all()
        serializer = self.serializer_class(chats, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        methods=["GET"],
        description="Get all messages for a specific chat.",
    )
    def retrieve(self, request, pk=None):
        chat = Chat.objects.prefetch_related("chatmessage_set").get(pk=pk)
        chat_serializer = self.serializer_class(chat, context={'request': request})
        message_serializer = ChatMessageSerializer(chat.chatmessage_set.all().order_by('date_published'), many=True)
        data = {
            'chat': chat_serializer.data,
            'messages': message_serializer.data
        }
        return Response(data)


@extend_schema(tags=["Messages"])
class MessageViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    serializer_class = ChatMessageSerializer
    queryset = ChatMessage.objects.all()
    permission_classes = [IsAuthenticated]

    http_method_names = ['post', 'head', 'options', 'put', 'delete']

    def create(self, request):
        message = self.serializer_class(data=request.data)
        if message.is_valid():
            obj = message.save()
            obj.sender = self.request.user
            chat_set = Chat.objects.filter(users__in=[obj.recipient]).filter(users__in=[self.request.user])
            print(chat_set.count())
            if chat_set.count() == 0:
                chat = Chat.objects.create()
                chat.users.set([obj.sender, obj.recipient])
                chat.save()
            else:
                chat = chat_set.first()
            obj.chat = chat
            obj.save()
            message = ChatMessageSerializer(obj)
        return Response(message.data)
