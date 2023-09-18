from drf_psq import PsqMixin, Rule
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, OpenApiExample
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status

from builder.permissions import IsMyApartment
from builder.serializers import *
from client.models import *
from django_filters import rest_framework as filters

from client.permissions import IsBuilder, IsClient


@extend_schema(tags=["Complexes"])
class ComplexViewSet(
    PsqMixin,
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):
    parser_classes = [MultiPartParser]
    serializer_class = ComplexSerializer
    queryset = Complex.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'get', 'patch']
    psq_rules = {
        ('create', 'my_complex', 'update_my_complex'): [
            Rule([IsBuilder], ComplexSerializer),
        ],
    }

    @extend_schema(
        description="Add complex for authenticated builder. Permissions: IsBuilder"
    )
    def create(self, request, *args, **kwargs):
        if hasattr(self.request.user, 'complex'):
            return Response("Комплекс уже создан для текущего пользователя")
        serializer = self.serializer_class(data=request.data, context={'builder': self.request.user})
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        description="Get complex for a authenticated builder. Permissions: IsBuilder",
    )
    @action(methods=["get"], detail=False, url_path="my_complex")
    def my_complex(self, request, *args, **kwargs):
        if not hasattr(self.request.user, 'complex'):
            return Response("Сначала создайте комплекс", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = self.serializer_class(self.queryset.get(builder=request.user))
        return Response(serializer.data)

    @extend_schema(
        methods=["Patch"],
        description="Update complex of authenticated builder. Permissions: IsBuilder",
    )
    @action(methods=["patch"], detail=False, url_path="update_my_complex")
    def update_my_complex(self, request, *args, **kwargs):
        if not hasattr(self.request.user, 'complex'):
            return Response("Сначала создайте комплекс", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = self.serializer_class(request.user.complex, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        description="Get list of favourite complexes for a authenticated user. Permissions: IsAuthenticated",
    )
    @action(methods=["get"], detail=False, url_path="my_favorite_complexes")
    def my_favorite_complexes_list(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user.favorite_complexes.all(), many=True)
        return Response(serializer.data)

    @extend_schema(
        description="(Add to favorites)/(Remove from favorites) complex for a authenticated user. Permissions: "
                    "IsAuthenticated",
    )
    @action(methods=["post"], detail=True, url_path="switch_complex_favorite", serializer_class=None)
    def switch_complex_favorite(self, request, *args, **kwargs):
        if self.get_object() in request.user.favorite_complexes.all():
            request.user.favorite_complexes.remove(self.get_object())
            return Response("Успешно удалён")
        request.user.favorite_complexes.add(self.get_object())
        return Response("Успешно добавлен")


@extend_schema(tags=["Corp"])
class CorpViewSet(viewsets.ModelViewSet):
    serializer_class = CorpSerializer
    queryset = Corp.objects.all()
    permission_classes = [IsBuilder]
    http_method_names = ['post', 'patch', 'delete']
    parser_classes = [JSONParser]

    @extend_schema(
        description="Create corpus for own complex by authenticated builder. Permissions: "
                    "IsBuilder",
    )
    def create(self, request, *args, **kwargs):
        if not hasattr(self.request.user, 'complex'):
            return Response("Сначала создайте комплекс", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)

    @extend_schema(
        description="Update corpus for own complex by authenticated builder. Permissions: "
                    "IsBuilder",
    )
    def partial_update(self, request, *args, **kwargs):
        if not hasattr(self.request.user, 'complex'):
            return Response("Сначала создайте комплекс", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().partial_update(request, args, kwargs)

    @extend_schema(
        description="Delete corpus for own complex by authenticated builder. Permissions: "
                    "IsBuilder",
    )
    def destroy(self, request, *args, **kwargs):
        if not hasattr(self.request.user, 'complex'):
            return Response("Сначала создайте комплекс", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, args, kwargs)


@extend_schema(tags=["News for Complex"])
class NewsViewSet(viewsets.ModelViewSet):
    serializer_class = NewsSerializer
    queryset = News.objects.all()
    permission_classes = [IsBuilder]
    http_method_names = ['patch', 'post', 'delete']
    parser_classes = [JSONParser]

    @extend_schema(
        description="Create news for own complex by authenticated builder. Permissions: "
                    "IsBuilder",
    )
    def create(self, request):
        if not hasattr(self.request.user, 'complex'):
            return Response("Сначала создайте комплекс", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(complex=request.user.complex)
        return Response(serializer.data, status.HTTP_201_CREATED)

    @extend_schema(
        description="Update news for own complex by authenticated builder. Permissions: "
                    "IsBuilder",
    )
    def partial_update(self, request, *args, **kwargs):
        if not hasattr(self.request.user, 'complex'):
            return Response("Сначала создайте комплекс", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().partial_update(request, args, kwargs)

    @extend_schema(
        description="Delete news for own complex by authenticated builder. Permissions: "
                    "IsBuilder",
    )
    def destroy(self, request, *args, **kwargs):
        if not hasattr(self.request.user, 'complex'):
            return Response("Сначала создайте комплекс", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, args, kwargs)


@extend_schema(tags=["Benefits for Complex"])
class BenefitViewSet(viewsets.GenericViewSet):
    serializer_class = BenefitSerializer
    queryset = Benefit.objects.all()
    permission_classes = [IsBuilder]
    http_method_names = ['patch', 'post']
    parser_classes = [JSONParser]

    @extend_schema(description='Permissions: IsBuilder.\n'
                               "Update benefits for own complex of authenticated builder.")
    @action(methods=['patch'], detail=False, url_path="update_for_my_complex",
            url_name="update_for_my_complex")
    def update_for_my_complex(self, request, *args, **kwargs):
        if not hasattr(self.request.user, 'complex'):
            return Response("Сначала создайте комплекс", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = self.serializer_class(request.user.complex.benefit, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(complex=request.user.complex)
        return Response(serializer.data, status.HTTP_201_CREATED)


class ApartmentFilter(filters.FilterSet):
    price = filters.RangeFilter()
    square = filters.RangeFilter()
    price_per_m2 = filters.RangeFilter()

    class Meta:
        model = Apartment
        fields = ['price', 'square', 'price_per_m2']


@extend_schema(tags=["Apartments"])
class ApartmentViewSet(
    PsqMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ApartmentFilter
    parser_classes = [MultiPartParser]
    http_method_names = ['patch', 'get', 'post', 'delete']
    psq_rules = {
        ('add_to_my_complex', 'for_my_complex_list', 'unmoderated_for_my_complex',
         'moderate_for_my_complex', 'partial_update', 'delete', 'retrieve'): [
            Rule([IsBuilder], ApartmentSerializer),
        ],
        ('switch_booking',): [
            Rule([IsMyApartment], ApartmentSerializer),
        ],
    }

    @extend_schema(description='Permissions: IsBuilder.\n'
                               "Create new apartment for own complex of authenticated builder.")
    @action(methods=['post'], detail=False, url_path="add_to_my_complex",
            url_name="add_to_my_complex")
    def add_to_my_complex(self, request, *args, **kwargs):
        if not hasattr(self.request.user, 'complex'):
            return Response("Сначала создайте комплекс", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = self.serializer_class(data=request.data,
                                           context={'user': request.user, 'complex': request.user.complex,
                                                    'is_moderated': True})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)

    @extend_schema(responses=ApartmentSerializer(many=True), description='Permissions: IsBuilder.\n'
                                                                         "Get all apartments list for own complex of "
                                                                         "authenticated builder.")
    @action(methods=['get'], detail=False, url_path="for_my_complex_list",
            url_name="for_my_complex_list")
    def for_my_complex_list(self, request, *args, **kwargs):
        if not hasattr(self.request.user, 'complex'):
            return Response("Сначала создайте комплекс", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        filtered_queryset = self.filterset_class(request.GET, queryset=self.get_queryset()).qs
        filtered_queryset = filtered_queryset.filter(complex=request.user.complex, is_moderated=True)
        complex = Complex.objects.prefetch_related('corps').get(builder=request.user)
        result = {}
        for i, corp in enumerate(complex.corps.prefetch_related('sections').all()):
            if i == 0:
                result = corp.sections.all()
            result = result.union(corp.sections.all())
        if len(result):
            serializer = ApartmentListSerializer(result.order_by('corp_id'), many=True,
                                                 context={'filtered_queryset': filtered_queryset})

            return Response(data=serializer.data)
        else:
            return Response([])

        return Response(data=serializer.data)

    @extend_schema(responses=ApartmentSerializer(many=True), description='Permissions: IsAuthenticated.\n'
                                                                         "Get all moderated apartments for specific complex by id.")
    @action(methods=['get'], detail=False, url_path="for_complex/(?P<complex_id>[^/.]+)",
            url_name="for_complex")
    def for_complex(self, request, *args, **kwargs):
        filtered_queryset = self.filterset_class(request.GET, queryset=self.get_queryset()).qs
        filtered_queryset = filtered_queryset.filter(is_moderated=True, complex=self.kwargs['complex_id'])
        complex = Complex.objects.prefetch_related('corps').get(pk=self.kwargs['complex_id'])
        result = {}
        for i, corp in enumerate(complex.corps.prefetch_related('sections').all()):
            if i == 0:
                result = corp.sections.all()
            result = result.union(corp.sections.all())
        if len(result):
            serializer = ApartmentListSerializer(result.order_by('corp_id'), many=True,
                                                 context={'filtered_queryset': filtered_queryset})
            return Response(data=serializer.data)
        else:
            return Response([])
        return Response(data=serializer.data)

    @extend_schema(description='Permissions: IsBuilder.\n'
                               "Get all unmoderated apartments for own complex of authenticated builder.")
    @action(methods=['get'], detail=False, url_path="unmoderated_for_my_complex",
            url_name="unmoderated_for_my_complex")
    def unmoderated_for_my_complex(self, request, *args, **kwargs):
        if not hasattr(self.request.user, 'complex'):
            return Response("Сначала создайте комплекс", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        apartments = self.queryset.filter(is_moderated=None)
        serializer = self.serializer_class(apartments, many=True)
        return Response(data=serializer.data)

    @extend_schema(description='Permissions: IsBuilder.\n'
                               "Moderate apartment by id for own complex of authenticated builder.",
                   request=ApartmentModerationSerializer,
                   responses=ApartmentModerationSerializer
                   )
    @action(methods=['patch'], detail=True, url_path="moderate_for_my_complex",
            url_name="moderate_for_my_complex")
    def moderate_for_my_complex(self, request, *args, **kwargs):
        if not hasattr(self.request.user, 'complex'):
            return Response("Сначала создайте комплекс", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        apartment = Apartment.objects.get(pk=self.kwargs['pk'])
        serializer = ApartmentModerationSerializer(apartment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="(Add apartment to booked)/(Remove apartment from booked) for a authenticated user. Permissions: "
                    "IsAuthenticated",
    )
    @action(methods=['patch'], detail=True, url_path="switch_booking", serializer_class=None,
            url_name="switch_booking")
    def switch_booking(self, request, *args, **kwargs):
        try:
            apartment = self.queryset.get(pk=self.kwargs['pk'])
        except Apartment.DoesNotExist:
            return Response("Аппартаменты не найдены")
        if apartment.is_booked:
            apartment.is_booked = False
            apartment.save()
            return Response("Успешно снята бронь")

        else:
            apartment.is_booked = True
            apartment.save()
            return Response("Успешно забронировано")


@extend_schema(tags=["Chessboards"])
@extend_schema(
    methods=["GET"], description="Get all apartment. Permissions: IsAuthenticated"
)
@extend_schema(methods=["PUT", "PATCH"], description="Update specific apartment.")
class ChessboardViewSet(
    PsqMixin,
    viewsets.GenericViewSet
):
    serializer_class = ChessBoardSerializer
    queryset = Complex.objects.all()
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]
    psq_rules = {
        ('chessboards_for_my_complex',): [
            Rule([IsBuilder], ChessBoardSerializer),
        ],
        ('add_to_chessboard',): [
            Rule([IsClient], ChessBoardSerializer),
        ],
    }

    @extend_schema(description='Permissions: IsBuilder.\n'
                               "Get all chessboards for own complex of authenticated builder.")
    @action(methods=['get'], detail=False, url_path="chessboards_for_my_complex", url_name="chessboards_for_my_complex")
    def chessboards_for_my_complex(self, request, *args, **kwargs):
        if not hasattr(self.request.user, 'complex'):
            return Response("Сначала создайте комплекс", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        complex = Complex.objects.prefetch_related('corps').get(builder=request.user)
        result = {}
        for i, corp in enumerate(complex.corps.prefetch_related('sections').all()):
            if i == 0:
                result = corp.sections.all()
            result = result.union(corp.sections.all())
        if len(result):
            serializer = self.serializer_class(result.order_by('corp_id'), many=True)

            return Response(data=serializer.data)
        else:
            return Response([])

    @extend_schema(description='Permissions: IsAuthenticated.\n'
                               "Get all chessboards for complex.")
    @action(methods=['get'], detail=True, url_path="chessboards_for_complex", url_name="chessboards_for_complex")
    def chessboards_for_complex(self, request, *args, **kwargs):
        try:
            complex = Complex.objects.prefetch_related('corps').get(pk=self.kwargs['pk'])
        except Complex.DoesNotExist:
            return Response("Комплекс отсутствует")
        result = Section.objects.none()
        for i, corp in enumerate(complex.corps.prefetch_related('sections').all()):
            if i == 0:
                result = corp.sections.all()
            result = result.union(corp.sections.all())
        serializer = self.serializer_class(result.order_by('corp_id'), many=True)

        return Response(data=serializer.data)

    @extend_schema(methods=["POST"], description="Create new apartment for adding to chessboard.Permissions: IsClient",
                   request=ApartmentSerializer,
                   responses=ApartmentSerializer
                   )
    @action(methods=['post'], detail=False, url_path="add_to_chessboard/(?P<complex_id>[^/.]+)",
            url_name="add_to_chessboard")
    def add_to_chessboard(self, request, complex_id, *args, **kwargs):
        complex = Complex.objects.get(pk=complex_id)
        serializer = ApartmentSerializer(data=request.data, context={'user': request.user, 'complex': complex,
                                                                     'is_moderated': None})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
