from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from client.serializers import *


@extend_schema(tags=["Adverts"])
class AdvertViewSet(viewsets.ModelViewSet):
    serializer_class = AdvertSerializer
    queryset = Advert.objects.all()


@extend_schema(tags=["Subscriptions"])
class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()


@extend_schema(tags=["Promotions"])
class PromotionViewSet(viewsets.ModelViewSet):
    serializer_class = PromotionSerializer
    queryset = Promotion.objects.all()


@extend_schema(tags=["Filters"])
class FilterViewSet(viewsets.ModelViewSet):
    serializer_class = FilterSerializer
    queryset = Filter.objects.all()


@extend_schema(tags=["Chats"])
class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()


@extend_schema(tags=["Messages"])
class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    queryset = ChatMessage.objects.all()
