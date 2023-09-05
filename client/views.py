from dateutil.relativedelta import relativedelta
from django.db.models import Q
from drf_psq import Rule, PsqMixin
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from client.permissions import IsMyAnnouncement, IsBuilder, IsClient, IsMyPromotion
from client.serializers import *
from users.models import *
from django_filters import rest_framework as filters
from builder.models import *


class AnnouncementFilter(filters.FilterSet):
    address = filters.CharFilter(field_name='address', lookup_expr='iexact')
    grounds_doc = filters.MultipleChoiceFilter(field_name='grounds_doc', choices=ApartmentDocument.choices)
    layout = filters.MultipleChoiceFilter(field_name='layout', choices=ApartmentLayout.choices)
    room_count = filters.MultipleChoiceFilter(field_name='room_count', choices=ApartmentRooms.choices)
    price = filters.RangeFilter()
    square = filters.RangeFilter()
    payment_type = filters.MultipleChoiceFilter(field_name='payment_type', choices=PaymentTypes.choices)
    appointment = filters.MultipleChoiceFilter(field_name='appointment', choices=ApartmentAppointment.choices)
    living_condition = filters.MultipleChoiceFilter(field_name='living_condition', choices=ApartmentCondition.choices)

    class Meta:
        model = Announcement
        fields = [
            'address',
            'layout',
            'grounds_doc',
            'room_count',
            'price',
            'square',
            'appointment',
            'payment_type',
            'living_condition',
        ]


@extend_schema(tags=["Moderation-Announcements"])
class AnnouncementModerationViewSet(
    PsqMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = AnnouncementModerationSerializer
    queryset = Announcement.objects.filter(is_moderated=None)
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch']
    filterset_class = AnnouncementFilter
    parser_classes = [JSONParser]
    psq_rules = {
        ('list', 'update'): [
            Rule([IsAdminUser], AnnouncementModerationSerializer),
        ],
    }

    @extend_schema(description='Permissions: IsAdmin.\n'
                               "Moderate announcement by id.")
    def update(self, request, *args, **kwargs):
        return super().update(request, args, kwargs)

    @extend_schema(description='Permissions: IsAdmin.\n'
                               "Get all unmoderated announcements list.")
    def list(self, request, *args, **kwargs):
        return super().list(self, request, args, kwargs)


@extend_schema(tags=["Announcements"])
class AnnouncementViewSet(
    PsqMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = AnnouncementSerializer
    queryset = Announcement.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    filterset_class = AnnouncementFilter
    parser_classes = [JSONParser]
    psq_rules = {
        ('partial_update',): [
            Rule([IsAdminUser | IsMyAnnouncement], AnnouncementSerializer),
        ],
        ('create',): [
            Rule([IsBuilder | IsClient], AnnouncementSerializer),
        ],
        ('destroy',): [
            Rule([IsMyAnnouncement], AnnouncementSerializer),
        ],
        ('retrieve', 'list', 'switch_complex_favorite'): [
            Rule([IsAuthenticated], AnnouncementSerializer),
        ],
        ('my_announcements',): [
            Rule([IsClient], AnnouncementSerializer),
        ],
    }

    @extend_schema(description='Permissions: IsAuthenticated.\n'
                               "(Add to favorites)/(Remove from favorites) announcement by id for current user.")
    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.watched_count = obj.watched_count + 1
        obj.save()
        return super().retrieve(request, args, kwargs)

    @extend_schema(description='Permissions: IsAuthenticated.\n'
                               "(Add to favorites)/(Remove from favorites) announcement by id for current user.")
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)

    @extend_schema(description='Permissions: IsAuthenticated & IsClient.\n'
                               "Get all announcements list for current user.")
    @action(methods=['get'], detail=False)
    def my_announcements(self, request, *args, **kwargs):
        filtered_queryset = self.filterset_class(request.GET, queryset=self.get_queryset()).qs
        announcements = filtered_queryset.filter(client=request.user)
        serializer = self.serializer_class(announcements, many=True)
        return Response(serializer.data)

    @extend_schema(description='Permissions: IsAuthenticated.\n'
                               "(Add to favorites)/(Remove from favorites) announcement by id for current user.")
    @action(methods=["post"], detail=True, url_path="switch_announcement_favorite")
    def switch_complex_favorite(self, request, *args, **kwargs):
        if self.get_object() in request.user.favorite_announcements.all():
            request.user.favorite_announcements.remove(self.get_object())
            return Response("Успешно удалён")
        request.user.favorite_announcements.add(self.get_object())
        return Response("Успешно добавлен")

    @extend_schema(description='Permissions: IsMyAnnouncement | IsAdmin.\n'
                               "Update announcement by id for current user or admin.")
    def update(self, request, *args, **kwargs):
        return super().update(request, args, kwargs)


@extend_schema(tags=["Subscriptions"])
class SubscriptionViewSet(
    PsqMixin,
    viewsets.GenericViewSet
):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    psq_rules = {
        ('my_subscription', 'renewal', 'switch_autorenewal'): [
            Rule([IsBuilder | IsClient], AnnouncementSerializer),
        ]
    }

    @extend_schema(description='Permissions: IsAuthenticated & IsMyProfile(only client, not admin or developer).\n'
                               'Get subscription info for current user')
    @action(
        detail=False,
        methods=["get"],
        url_path="my_subscription",
    )
    def my_subscription(self, request, *args, **kwargs):
        subscription = request.user.subscription
        serializer = self.serializer_class(subscription)
        return Response(data=serializer.data)

    @extend_schema(description='Permissions: IsAuthenticated & IsMyProfile(only client, not admin or developer).\nRenew'
                               ' subscription for current user')
    @action(
        detail=False,
        methods=["patch"],
        url_path="renewal",
    )
    def renewal(self, request, *args, **kwargs):
        subscription = request.user.subscription
        subscription.expiration_date = subscription.expiration_date + relativedelta(months=1)
        subscription.save()

        return Response("Подписка успешно продлена на месяц")

    @extend_schema(description='Permissions: IsAuthenticated & IsMyProfile(only client, not admin or developer).\n'
                               'Switch subscription auto-renewal for current user')
    @action(
        detail=False,
        methods=["PATCH"],
        url_path="switch_autorenewal",
    )
    def switch_autorenewal(self, request, *args, **kwargs):
        subscription = request.user.subscription
        if subscription.auto_renewal is False:
            subscription.auto_renewal = True
            subscription.save()
            return Response("Автопродление подписки включено")
        else:
            subscription.auto_renewal = False
            subscription.save()
            return Response("Автопродление подписки выключено")


@extend_schema(tags=["Promotions"])
class PromotionViewSet(
    PsqMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PromotionSerializer
    queryset = Promotion.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'post', 'get', 'update']
    parser_classes = [JSONParser]
    psq_rules = {
        ('create',): [
            Rule([IsBuilder | IsClient], PromotionSerializer),
        ],
        ('retrieve', 'partial_update'): [
            Rule([IsMyPromotion], PromotionSerializer),
        ]
    }

    @extend_schema(description='Permissions: IsAuthenticated.\n'
                               'Create promotion for some announcement.')
    def create(self, request, *args, **kwargs):
        return super().create(request, args, kwargs)

    @extend_schema(description='Permissions: IsAuthenticated & IsMyPromotion.\n'
                               'Get promotion info by announcement id')
    def retrieve(self, request, *args, **kwargs):
        promotion = Promotion.objects.get(pk=kwargs["pk"])
        serializer = self.serializer_class(promotion)
        return Response(serializer.data)

    @extend_schema(description='Permissions: IsAuthenticated & IsMyPromotion.\n'
                               'Update promotion info by announcement id')
    def partial_update(self, request, *args, **kwargs):
        instance = Promotion.objects.get(pk=kwargs["pk"])
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@extend_schema(tags=["Filters"])
class FilterViewSet(viewsets.ModelViewSet):
    serializer_class = FilterSerializer
    queryset = Filter.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'delete', 'get']
    parser_classes = [JSONParser]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        filters = request.user.filters.all()
        serializer = self.serializer_class(filters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        try:
            filter = request.user.filters.get(pk=kwargs['pk'])
        except Filter.DoesNotExist:
            return Response('Фильтр не найден')
        serializer = self.serializer_class(filter)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='announcements_list',
            url_name='announcements_list')
    def announcements_list(self, request, *args, **kwargs):
        filter = Filter.objects.get(pk=kwargs["pk"])
        announcemements = Announcement.objects.all()
        qs = []
        if filter.address:
            qs.append(Q(address=filter.address))
        if filter.appointment:
            qs.append(Q(appointment=filter.appointment))
        if filter.condition:
            qs.append(Q(condition=filter.condition))
        if filter.grounds_doc:
            qs.append(Q(grounds_doc=filter.grounds_doc))
        if filter.layout:
            qs.append(Q(layout=filter.layout))
        if filter.payment_type:
            qs.append(Q(payment_type=filter.payment_type))
        if filter.room_count:
            qs.append(Q(room_count=filter.room_count))
        if filter.min_price:
            qs.append(Q(price__gte=filter.min_price))
        if filter.max_price:
            qs.append(Q(price__lte=filter.max_price))
        if filter.min_square:
            qs.append(Q(square__gte=filter.min_square))
        if filter.max_square:
            qs.append(Q(square__lte=filter.max_square))
        q = Q()
        for item in qs:
            q = q & item
        announcements = announcemements.filter(q)

        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(
            data={
                'announcements_count': announcements.count(),
                'announcements': serializer.data,
            },
            status=status.HTTP_200_OK)


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
    parser_classes = [JSONParser]

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
    parser_classes = [MultiPartParser]

    http_method_names = ['post', 'head', 'options', 'put', 'delete']

    @extend_schema(description='Permissions: IsAuthenticated.\n'
                               'Send message to some user.')
    def create(self, request):
        message = self.serializer_class(data=request.data)
        if message.is_valid():
            obj = message.save()
            obj.sender = self.request.user
            chat_set = Chat.objects.filter(users__in=[obj.recipient]).filter(users__in=[self.request.user])
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

    @extend_schema(description='Permissions: IsAuthenticated.\n'
                               'Update message.')
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(description='Permissions: IsAuthenticated.\n'
                               'Destroy message.')
    def destroy(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


@extend_schema(tags=["Complaints"])
class ComplaintViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    serializer_class = ComplaintSerializer
    queryset = Complaint.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    http_method_names = ['post', 'head', 'options', 'get']

    @action(methods=['get'], detail=False, url_path='announcement_complaint_list/(?P<announcement_id>[^/.]+)',
            url_name='announcement_complaint_list')
    def announcement_complaint_list(self, request, *args, **kwargs):
        complaints = Complaint.objects.filter(announcement_id=kwargs["announcement_id"])
        serializer = self.serializer_class(complaints, many=True)
        return Response(serializer.data)
