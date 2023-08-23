from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from builder.serializers import GallerySerializer, ComplexSerializer
from client.models import *
from users.models import CustomUser


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = "__all__"


class AnnouncementSerializer(serializers.ModelSerializer):
    gallery = GallerySerializer(read_only=True)
    promotion = PromotionSerializer(read_only=True)

    class Meta:
        model = Announcement
        exclude = ('client', 'is_moderated', 'watched_count', 'is_actual', 'moderation_status')

    def create(self, validated_data):
        gallery = Gallery.objects.create()
        instance = Announcement.objects.create(**validated_data, gallery=gallery, client=self.context['user'])
        return instance


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        exclude = ('chat', 'sender')


class ChatSerializer(serializers.ModelSerializer):
    # Поле в котором будет храниться последнее сообщение написаное в чате
    # Если нужно добавить дополнительное поле используем SerializerMethodField
    last_message = serializers.SerializerMethodField('is_last_message')

    def is_last_message(self, obj):
        return ChatMessage.objects.filter(chat_id=obj.id).order_by('-date_published')[0].content

    title = serializers.SerializerMethodField('is_title')

    def is_title(self, obj):
        user = self.context['request'].user
        try:
            recipient = Chat.objects.get(pk=obj.id).users.exclude(id=user.id).get()
            result = f"{recipient.last_name} {recipient.first_name}"

        except CustomUser.DoesNotExist:
            result = "Deleted Account"
        return result

    class Meta:
        model = Chat
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"


class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        exclude = ('client',)

    def create(self, validated_data):
        instance = Filter.objects.create(**validated_data, client=self.context['user'])
        return instance


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = "__all__"
