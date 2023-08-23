from dateutil.relativedelta import relativedelta
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
    http_method_names = ['get', 'post', 'patch', 'delete', 'options', 'head']
    filterset_class = AnnouncementFilter

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)

    @action(methods=['get'], detail=False, url_path="unmoderated_announcements_list",
            url_name="unmoderated_announcements_list")
    def unmoderated_announcements_list(self, request, *args, **kwargs):
        filtered_queryset = self.filterset_class(request.GET, queryset=self.get_queryset()).qs
        announcements = filtered_queryset.filter(is_moderated=None)
        serializer = self.serializer_class(announcements, many=True)
        return Response(data=serializer.data)

    @extend_schema(
        methods=["GET"],
        description="Get all announcements for authenticated user.",
    )
    @action(methods=['get'], detail=False, url_path='my_announcements', url_name=None, )
    def my_announcements(self, request, *args, **kwargs):
        filtered_queryset = self.filterset_class(request.GET, queryset=self.get_queryset()).qs
        announcements = filtered_queryset.filter(client=request.user)
        serializer = self.serializer_class(announcements, many=True)
        return Response(serializer.data)

    @extend_schema(
        methods=["POST"],
        description="Get favourite announcements for a authenticated user. Permissions: IsAuthenticated",
    )
    @action(methods=["post"], detail=True, url_path="switch_announcement_favorite")
    def switch_complex_favorite(self, request, *args, **kwargs):
        if self.get_object() in request.user.favorite_announcements.all():
            request.user.favorite_announcements.remove(self.get_object())
            return Response("Успешно удалён")
        request.user.favorite_announcements.add(self.get_object())
        return Response("Успешно добавлен")


@extend_schema(tags=["Subscriptions"])
class SubscriptionViewSet(
    viewsets.GenericViewSet
):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        description="Subscription of authenticated user",
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="my_subscription",
    )
    def my_subscription(self, request, *args, **kwargs):
        subscription = request.user.subscription
        serializer = self.serializer_class(subscription)
        return Response(data=serializer.data)

    @extend_schema(
        methods=["PATCH"],
        description="Renewal subscription authenticated user",
    )
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

    @extend_schema(
        methods=["GET"],
        description="Get authenticated user profile",
    )
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
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PromotionSerializer
    queryset = Promotion.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'post', 'get']

    @action(methods=['get'], detail=False, url_path='(?P<announcement_id>[^/.]+)', )
    def get_promotion(self, request, *args, **kwargs):
        promotion = Promotion.objects.get(announcement_id=kwargs["announcement_id"])
        serializer = self.serializer_class(promotion)
        return Response(serializer.data)

    @action(methods=['PATCH'], detail=False, url_path='update/(?P<announcement_id>[^/.]+)', url_name='update_promotion')
    def update_promotion(self, request, *args, **kwargs):
        instance = Promotion.objects.get(announcement_id=kwargs["announcement_id"])
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


@extend_schema(tags=["Complaints"])
class ComplaintViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    serializer_class = ComplaintSerializer
    queryset = Complaint.objects.all()
    permission_classes = [IsAuthenticated]

    http_method_names = ['post', 'head', 'options', 'get']


    @action(methods=['get'], detail=False, url_path='announcement_complaint_list/(?P<announcement_id>[^/.]+)',
            url_name='announcement_complaint_list')
    def announcement_complaint_list(self, request, *args, **kwargs):
        complaints = Complaint.objects.filter(announcement_id=kwargs["announcement_id"])
        serializer = self.serializer_class(complaints, many=True)
        return Response(serializer.data)
