from drf_extra_fields.fields import Base64ImageField
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


class AnnouncementGallerySerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = GalleryAnnouncement
        fields = ('id', 'order', 'image')


class AnnouncementSerializer(serializers.ModelSerializer):
    images = AnnouncementGallerySerializer(many=True, required=False)
    main_photo = Base64ImageField()
    promotion = PromotionSerializer(read_only=True)
    apartment = serializers.PrimaryKeyRelatedField(required=False, queryset=Apartment.objects.all())

    class Meta:
        model = Announcement
        exclude = ('client', 'is_moderated', 'watched_count', 'is_actual', 'moderation_status', 'price_per_m2')

    def create(self, validated_data):
        if 'images' in validated_data:
            images_data = validated_data.pop('images')
            instance = Announcement.objects.create(**validated_data, client=self.context['user'])
            for image in images_data:
                GalleryAnnouncement.objects.create(announcement=instance, **image)
        else:
            instance = Announcement.objects.create(**validated_data, client=self.context['user'])
        return instance

    def update(self, instance, validated_data):
        if 'images' in validated_data:
            images_data = validated_data.pop('images')
            images = {img.id: img for img in instance.images.all()}
            for image_data in images_data:
                image_id = image_data.get('id', None)
                if image_id:
                    image = images.get(image_id, None)
                    if image:
                        image.order = image_data.get('order', image.order)
                        image.save()
                else:
                    GalleryAnnouncement.objects.create(announcement=instance, **image_data)

        instance.images.exclude(id__in=[img['id'] for img in images_data if 'id' in img]).delete()

        # instance.images.exclude(pk__in=imgs).delete()
        instance.save()
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
