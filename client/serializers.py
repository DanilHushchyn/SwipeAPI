from rest_framework import serializers

from builder.serializers import GallerySerializer, ComplexSerializer
from client.models import *
from users.models import CustomUser


class AnnouncementSerializer(serializers.ModelSerializer):
    gallery = GallerySerializer(read_only=True)

    class Meta:
        model = Announcement
        exclude = ('client', 'apartment', 'is_moderated')

    def create(self, validated_data):
        gallery = Gallery.objects.create()
        instance = Announcement.objects.create(**validated_data, gallery=gallery, client=self.context['user'], )
        return instance


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = "__all__"


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
        fields = "__all__"
