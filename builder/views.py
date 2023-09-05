from drf_psq import PsqMixin, Rule
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, OpenApiExample
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status

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
    http_method_names = ['post', 'get', 'put']
    psq_rules = {
        ('create', 'my_complex', 'update_my_complex'): [
            Rule([IsBuilder], ComplexSerializer),
        ],
    }
    """ПОТЕСТИТЬ CREATE Чтобы не больше одного ЖК на застройщика"""

    @extend_schema(
        description="Add complex for authenticated builder. Permissions: IsBuilder",
    )
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'builder': self.request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        description="Get complex for a authenticated user. Permissions: IsBuilder",
    )
    @action(methods=["get"], detail=False, url_path="my_complex")
    def my_complex(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset.get(builder=request.user))
        return Response(serializer.data)

    @extend_schema(
        methods=["PUT"],
        description="Update complex of authenticated builder. Permissions: IsBuilder",
    )
    @action(methods=["put"], detail=False, url_path="update_my_complex")
    def update_my_complex(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user.complex, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        description="Get favourite complexes for a authenticated user. Permissions: IsAuthenticated",
    )
    @action(methods=["get"], detail=False, url_path="my_favorite_complexes")
    def my_favorite_complexes_list(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user.favorite_complexes.all(), many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Get favourite complexes for a authenticated user. Permissions: IsAuthenticated",
    )
    @action(methods=["post"], detail=True, url_path="switch_complex_favorite")
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

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


@extend_schema(tags=["News for Complex"])
@extend_schema(
    methods=["GET"],
    description="Get news for all complexes. Permissions: IsAuthenticated",
)
@extend_schema(methods=["POST"], description="Create new news.")
class NewsViewSet(viewsets.ModelViewSet):
    serializer_class = NewsSerializer
    queryset = News.objects.all()
    permission_classes = [IsBuilder]
    http_method_names = ['patch', 'post', 'delete']
    parser_classes = [JSONParser]

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(complex=request.user.complex)
        return Response(serializer.data, status.HTTP_201_CREATED)


@extend_schema(tags=["Benefits for Complex"])
class BenefitViewSet(viewsets.GenericViewSet):
    serializer_class = BenefitSerializer
    queryset = Benefit.objects.all()
    permission_classes = [IsBuilder]
    http_method_names = ['patch', 'post']
    parser_classes = [JSONParser]

    @extend_schema(description='Permissions: IsBuilder.\n'
                               "Create benefits for complex of authenticated builder.")
    @action(methods=['post'], detail=False, url_path="create_for_my_complex",
            url_name="create_for_my_complex")
    def create_for_my_complex(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(complex=request.user.complex)
        return Response(serializer.data, status.HTTP_201_CREATED)

    @extend_schema(description='Permissions: IsBuilder.\n'
                               "Update benefits for complex of authenticated builder.")
    @action(methods=['patch'], detail=False, url_path="update_for_my_complex",
            url_name="update_for_my_complex")
    def update_for_my_complex(self, request, *args, **kwargs):
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
@extend_schema(
    methods=["GET"], description="Get all apartment. Permissions: IsAuthenticated"
)
@extend_schema(methods=["PUT", "PATCH"], description="Update specific apartment.")
@extend_schema(methods=["POST"], description="Create new apartment.")
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
    psq_rules = {
        ('add_to_my_complex', 'for_my_complex', 'unmoderated_for_my_complex', 'moderate_for_my_complex'): [
            Rule([IsBuilder], ApartmentSerializer),
        ],
    }

    @action(methods=['post'], detail=False, url_path="add_to_my_complex",
            url_name="add_to_my_complex")
    def add_to_my_complex(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'user': request.user, 'complex': request.user.complex,
                                                    'is_moderated': True})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)

    @action(methods=['get'], detail=False, url_path="for_my_complex",
            url_name="for_my_complex")
    def for_my_complex(self, request, *args, **kwargs):
        filtered_queryset = self.filterset_class(request.GET, queryset=self.get_queryset()).qs
        apartments = filtered_queryset.filter(complex=request.user.complex)
        serializer = self.serializer_class(apartments, many=True)
        return Response(data=serializer.data)

    @extend_schema(description='Permissions: IsAuthenticated.\n'
                               "(Add to favorites)/(Remove from favorites) announcement by id for current user.")
    @action(methods=['get'], detail=False, url_path="for_complex/(?P<complex_id>[^/.]+)",
            url_name="for_complex")
    def for_complex(self, request, *args, **kwargs):
        filtered_queryset = self.filterset_class(request.GET, queryset=self.get_queryset()).qs
        apartments = filtered_queryset.filter(complex=self.kwargs['complex_id'])
        serializer = self.serializer_class(apartments, many=True)
        return Response(data=serializer.data)

    @action(methods=['get'], detail=False, url_path="unmoderated_for_my_complex",
            url_name="unmoderated_for_my_complex")
    def unmoderated_for_my_complex(self, request, *args, **kwargs):
        apartments = self.queryset.filter(is_moderated=None)
        serializer = self.serializer_class(apartments, many=True)
        return Response(data=serializer.data)

    @extend_schema(description='Permissions: IsBuilder.\n'
                               "Moderate apartment by id.",
                   request=ApartmentModerationSerializer,
                   responses=ApartmentModerationSerializer
                   )
    @action(methods=['patch'], detail=True, url_path="moderate_for_my_complex",
            url_name="moderate_for_my_complex")
    def moderate_for_my_complex(self, request, *args, **kwargs):
        apartment = Apartment.objects.get(pk=self.kwargs['pk'])
        serializer = ApartmentModerationSerializer(apartment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path="switch_booking",
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
    parser_classes = [JSONParser]
    permission_classes = [IsAuthenticated]
    psq_rules = {
        ('chessboards_for_my_complex',): [
            Rule([IsBuilder], ChessBoardSerializer),
        ],
        ('add_to_chessboard',): [
            Rule([IsClient], ChessBoardSerializer),
        ],
    }

    @action(methods=['get'], detail=False, url_path="chessboards_for_my_complex", url_name="chessboards_for_my_complex")
    def chessboards_for_my_complex(self, request, *args, **kwargs):
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

    @extend_schema(methods=["POST"], description="Create new apartment for adding to chessboard.",
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
