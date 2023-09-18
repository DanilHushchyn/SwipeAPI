from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from builder.serializers import ComplexSerializer, ApartmentSerializer
from client.models import *
from users.models import CustomUser


class PromotionSerializer(serializers.ModelSerializer):
    announcement = serializers.PrimaryKeyRelatedField(queryset=Announcement.objects.all(), required=True)

    def create(self, validated_data):
        instance = Promotion.objects.create(**validated_data,
                                            expiration_date=(timezone.now() + timezone.timedelta(days=30)))
        return instance

    class Meta:
        model = Promotion
        exclude = ("expiration_date",)


class AnnouncementGallerySerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    id = serializers.IntegerField(read_only=False, required=False)

    class Meta:
        model = GalleryAnnouncement
        fields = ('id', 'order', 'image')


class AnnouncementModerationSerializer(serializers.ModelSerializer):
    images = AnnouncementGallerySerializer(many=True, read_only=True)
    promotion = PromotionSerializer(read_only=True)
    apartment = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Announcement
        fields = (
            'id',
            'is_moderated',
            'moderation_status',
            'promotion',
            'apartment',
            'images',
            'address',
            'description',
            'main_photo',
            'is_actual',
            'client',
            'grounds_doc',
            'appointment',
            'room_count',
            'layout',
            'living_condition',
            'kitchen_square',
            'balcony_or_loggia',
            'heating_type',
            'payment_type',
            'agent_commission',
            'communication_type',
            'payment_type',
            'date_published',
            'watched_count',
            'square',
            'price',
            'price_per_m2',
            'complex',
        )
        read_only_fields = [
            'id',
            'address',
            'description',
            'main_photo',
            'is_actual',
            'client',
            'grounds_doc',
            'appointment',
            'room_count',
            'layout',
            'living_condition',
            'kitchen_square',
            'balcony_or_loggia',
            'heating_type',
            'payment_type',
            'agent_commission',
            'communication_type',
            'payment_type',
            'date_published',
            'watched_count',
            'square',
            'price',
            'price_per_m2',
            'complex',
        ]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AnnouncementSerializer(serializers.ModelSerializer):
    images = AnnouncementGallerySerializer(many=True, required=False)
    main_photo = Base64ImageField(required=False)
    promotion = PromotionSerializer(read_only=True)
    apartment = serializers.PrimaryKeyRelatedField(required=False, queryset=Apartment.objects.all())

    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ['is_moderated', 'watched_count', 'is_actual', 'moderation_status', 'price_per_m2', 'client']

    def validate(self, data):
        if 'kitchen_square' in data and data['kitchen_square'] >= data['square']:
            raise serializers.ValidationError(
                {
                    'error_square': 'Площадь кухни не может превышать общую площадь'
                }
            )
        return data

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
            instance.images.exclude(id__in=[img['id'] for img in images_data if 'id' in img]).delete()
            for image_data in images_data:
                image_id = image_data.get('id', None)
                if image_id:
                    img = images.get(image_id, None)
                    if img:
                        img.order = image_data.get('order', img.order)
                        img.image = image_data.get('image', img.image)
                        img.save()
                else:
                    GalleryAnnouncement.objects.create(announcement=instance, **image_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.is_moderated = None
        instance.moderation_status = None
        instance.save()
        return instance


class AnnouncementReadingSerializer(AnnouncementSerializer):
    apartment = ApartmentSerializer(read_only=True)


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        exclude = ('chat', 'sender')


class ChatSerializer(serializers.ModelSerializer):
    # Поле в котором будет храниться последнее сообщение написаное в чате
    # Если нужно добавить дополнительное поле используем SerializerMethodField
    last_message = serializers.SerializerMethodField('is_last_message')

    def is_last_message(self, obj):
        if ChatMessage.objects.filter(chat_id=obj.id).count() > 0:
            return ChatMessage.objects.filter(chat_id=obj.id).order_by('-date_published')[0].content
        return "No messages yet"

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
        read_only_fields = ['sender', ]
