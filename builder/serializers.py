from rest_framework import serializers

from builder.models import *
import builder.serializers
from django.core import serializers as serialize_queryset

from django.db.models import QuerySet


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


class ApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        exclude = ('owner', 'complex', 'is_moderated', 'moderation_status')

    def create(self, validated_data):
        instance = Apartment.objects.create(**validated_data, owner=self.context['user'],
                                            is_moderated=self.context['is_moderated'],
                                            complex=self.context['complex'])
        return instance


class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        exclude = ['id', 'complex']


class FloorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Floor
        exclude = ('section', 'id')


class SewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sewer
        exclude = ('section', 'id')


class SectionSerializer(serializers.ModelSerializer):
    sewers = SewerSerializer(many=True, required=False)
    floors = FloorSerializer(many=True, required=False)

    class Meta:
        model = Section
        exclude = ('corp', 'id')

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


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = "__all__"


class GallerySerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Gallery
        fields = '__all__'
        read_only_fields = ['photos']


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"


class DocKitSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, read_only=True)

    class Meta:
        model = DocKit
        exclude = ('id',)
        read_only_fields = ['files']


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        exclude = ('date_published', 'complex')
        read_only_fields = ['id']


class ComplexSerializer(serializers.ModelSerializer):
    news = NewsSerializer(many=True, read_only=True)
    benefit = BenefitSerializer(required=False)
    corps = CorpSerializer(many=True, read_only=True)
    gallery = GallerySerializer(read_only=True)
    doc_kit = DocKitSerializer(read_only=True)

    class Meta:
        model = Complex
        exclude = ('builder',)
        read_only_fields = ['id', 'date_added', 'news', 'gallery', 'doc_kit']

    def update(self, instance, validated_data):
        if 'benefit' in validated_data:
            benefit = Benefit.objects.get(complex=instance)
            benefit.playground = validated_data['benefit'].get('playground', benefit.playground)
            benefit.school = validated_data['benefit'].get('school', benefit.school)
            benefit.tennis_court = validated_data['benefit'].get('tennis_court', benefit.tennis_court)
            benefit.shopping_mall = validated_data['benefit'].get('shopping_mall', benefit.shopping_mall)
            benefit.subway = validated_data['benefit'].get('subway', benefit.subway)
            benefit.park = validated_data['benefit'].get('park', benefit.park)
            benefit.save()
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.address = validated_data.get('address', instance.address)
        instance.coordinate = validated_data.get('coordinate', instance.coordinate)
        instance.main_photo = validated_data.get('main_photo', instance.main_photo)
        instance.min_price = validated_data.get('min_price', instance.min_price)
        instance.price_per_square = validated_data.get('price_per_square', instance.price_per_square)
        instance.min_squares = validated_data.get('min_squares', instance.min_squares)
        instance.max_squares = validated_data.get('max_squares', instance.max_squares)
        instance.square_price = validated_data.get('square_price', instance.square_price)
        instance.status = validated_data.get('status', instance.status)
        instance.level = validated_data.get('level', instance.level)
        instance.type = validated_data.get('type', instance.type)
        instance.material_type = validated_data.get('material_type', instance.material_type)
        instance.perimeter_status = validated_data.get('perimeter_status', instance.perimeter_status)
        instance.sea_destination_m = validated_data.get('sea_destination_m', instance.sea_destination_m)
        instance.ceiling_height_m = validated_data.get('ceiling_height_m', instance.ceiling_height_m)
        instance.gas = validated_data.get('gas', instance.gas)
        instance.heating = validated_data.get('heating', instance.heating)
        instance.electricity = validated_data.get('electricity', instance.electricity)
        instance.water_supply = validated_data.get('water_supply', instance.water_supply)
        instance.sewerage = validated_data.get('sewerage', instance.sewerage)
        instance.registration_type = validated_data.get('registration_type', instance.registration_type)
        instance.payment_type = validated_data.get('payment_type', instance.payment_type)
        instance.payment_target = validated_data.get('payment_target', instance.payment_target)
        instance.price_in_contract = validated_data.get('price_in_contract', instance.price_in_contract)
        instance.price_in_contract = validated_data.get('price_in_contract', instance.price_in_contract)

        instance.save()

        return instance
