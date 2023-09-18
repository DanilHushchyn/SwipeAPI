from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import _UnvalidatedField
from rest_framework.utils import html
from rest_framework.validators import UniqueTogetherValidator

from builder.models import *
import builder.serializers
from django.core import serializers as serialize_queryset

from django.db.models import QuerySet
from collections.abc import Mapping


class ChessBoardSerializer(serializers.Serializer):
    def to_representation(self, instance):
        custom_data = {
            'title': f"{instance.corp}, {instance.title}",
            'section_id': instance.id,
            'floors': list(instance.floors.values('id')),
            'floors_count': instance.floors.all().count(),
            'sewers': list(instance.sewers.values('id')),
            'sewers_count': instance.sewers.all().count(),
            'apartments': instance.apartments.filter(is_moderated=True).values('id', 'number', 'floor_id', 'sewer_id'),
        }
        return custom_data


class ApartmentListSerializer(serializers.Serializer):
    def to_representation(self, instance):
        custom_data = {
            'title': f"{instance.corp}, {instance.title}",
            'apartments': instance.apartments.filter(
                id__in=self.context['filtered_queryset'].values('id')
            ).values('id', 'number',
                     'floor_id',
                     'floor__title',
                     'sewer_id',
                     'sewer__number',
                     'square',
                     'scheme',
                     'price_per_m2',
                     'price',
                     'owner'),
        }
        return custom_data


class ApartmentModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = (
            'is_moderated',
            'moderation_status',
        )
        read_only_fields = [
            'number',
            'scheme',
            'section',
            'floor',
            'sewer',
            'complex',
            'owner',
            'square',
            'price',
            'is_booked',
            'price_per_m2',
        ]


class ApartmentSerializer(serializers.ModelSerializer):
    # scheme = Base64ImageField(required=False)

    class Meta:
        model = Apartment
        exclude = ('owner', 'complex', 'is_moderated', 'moderation_status', 'price_per_m2')
        validators = [
            UniqueTogetherValidator(
                queryset=Apartment.objects.all(),
                fields=['floor', 'sewer'],
                message='Эта комбинация floor_id и sewer_id уже занята, выберите иное расположение для ваших апартаментов в ЖК'
            )
        ]

    def create(self, validated_data):
        instance = Apartment.objects.create(**validated_data, owner=self.context['user'],
                                            is_moderated=self.context['is_moderated'],
                                            complex=self.context['complex'])
        return instance

    def validate(self, data):
        """
        Check that start is before finish.
        """
        section = Section.objects.prefetch_related('floors', 'sewers').get(pk=data['section'].id)
        floor = Floor.objects.prefetch_related('apartments').get(pk=data['floor'].id)
        sewer = Sewer.objects.get(pk=data['sewer'].id)
        if floor.id not in section.floors.all().values_list('id', flat=True):
            raise serializers.ValidationError(
                "Объект floor не ссылается на указанный объект section. Проверьте правильность ввода данных")
        if sewer.id not in section.sewers.all().values_list('id', flat=True):
            raise serializers.ValidationError(
                "Объект sewer не ссылается на указанный объект section. Проверьте правильность ввода данных")
        if floor.apartments.count() >= section.sewers.count():
            raise serializers.ValidationError(
                "На данном этаже уже находится максимальное количество апартаментов")

        return data


class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        exclude = ['id', 'complex']


class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        exclude = ('section',)


class SewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sewer
        exclude = ('section',)


class SectionSerializer(serializers.ModelSerializer):
    sewers = SewerSerializer(many=True, required=False)
    floors = FloorSerializer(many=True, required=False)

    class Meta:
        model = Section
        exclude = ('corp',)

    def create(self, validated_data):
        instance = Section.objects.create(title=validated_data['title'], corp_id=self.context['corp_id'])
        if 'sewers' in validated_data:
            sewers = validated_data.pop('sewers')
            for data in sewers:
                Sewer.objects.create(section=instance, **data)
        if 'floors' in validated_data:
            floors = validated_data.pop('floors')
            for data in floors:
                Floor.objects.create(section=instance, **data)
        return instance


class CorpSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, required=False)

    class Meta:
        model = Corp
        exclude = ("complex",)

    def create(self, validated_data):
        instance = Corp.objects.create(title=validated_data.get('title'), complex=self.context["request"].user.complex)
        if 'sections' in validated_data:
            sections = validated_data.pop('sections')
            for data in sections:
                section = SectionSerializer(data=data, context={'corp_id': instance.id})
                section.is_valid(raise_exception=True)
                section.save()

        return instance

    def update(self, instance, validated_data):
        if 'sections' in validated_data:
            sections = validated_data.pop('sections')
            instance.sections.all().delete()
            for data in sections:
                section = SectionSerializer(data=data, context={'corp_id': instance.id})
                section.is_valid(raise_exception=True)
                section.save()
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        return instance


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        exclude = ('date_published', 'complex')
        read_only_fields = ['id']


class СomplexGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryComplex
        fields = ('id', 'image')


class СomplexDocKitSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocKitComplex
        fields = ('id', 'file')


class ComplexSerializer(serializers.ModelSerializer):
    news = NewsSerializer(many=True, read_only=True)
    benefit = BenefitSerializer(read_only=True)
    corps = CorpSerializer(many=True, read_only=True)
    images = СomplexGallerySerializer(read_only=True, many=True)
    documents = СomplexDocKitSerializer(read_only=True, many=True)
    gallery = serializers.ListField(child=serializers.ImageField(required=False), write_only=True,
                                    required=False,
                                    allow_empty=True,
                                    )
    dockit = serializers.ListField(child=serializers.FileField(required=False), write_only=True,
                                   allow_empty=True,
                                   required=False)

    class Meta:
        model = Complex
        fields = '__all__'
        read_only_fields = ['id', 'date_added', 'news', 'images', 'documents', 'min_price', 'builder']

    def create(self, validated_data):
        gallery = validated_data.pop('gallery', False)
        dockit = validated_data.pop('dockit', False)
        instance = Complex.objects.create(
            **validated_data, builder=self.context.get('builder')
        )
        if gallery:
            for image in gallery:
                GalleryComplex.objects.create(
                    image=image, complex=instance
                )
        if dockit:
            for doc in dockit:
                DocKitComplex.objects.create(
                    file=doc, complex=instance
                )
        Benefit.objects.create(complex=instance)
        return instance

    def update(self, instance: Complex, validated_data):

        if 'gallery' in validated_data:
            gallery = validated_data.pop('gallery', False)

            if gallery:
                instance.images.all().delete()
                for image in gallery:
                    GalleryComplex.objects.create(
                        image=image, complex=instance
                    )
        if 'dockit' in validated_data:
            dockit = validated_data.pop('dockit', False)
            if dockit:
                instance.documents.all().delete()
                for doc in dockit:
                    DocKitComplex.objects.create(
                        file=doc, complex=instance
                    )
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
