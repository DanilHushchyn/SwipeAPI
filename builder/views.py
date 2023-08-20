from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status

from builder.serializers import *
from client.models import *


@extend_schema(tags=["Complexes"])
class ComplexViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    serializer_class = ComplexSerializer
    queryset = Complex.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'get', 'put']

    @extend_schema(
        methods=["GET"],
        description="Get complex for a authenticated user. Permissions: IsAuthenticated",
    )
    @action(methods=["get"], detail=False, url_path="my_complex")
    def my_complex(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset.get(builder=request.user))
        return Response(serializer.data)

    @extend_schema(
        methods=["PUT"],
        description="Update complex of authenticated user. Permissions: IsAuthenticated",
    )
    @action(methods=["put"], detail=False, url_path="update_my_complex")
    def update_my_complex(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user.complex, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        methods=["GET"],
        description="Get favourite complexes for a authenticated user. Permissions: IsAuthenticated",
    )
    @action(methods=["get"], detail=False, url_path="my_favorite_complexes")
    def my_favorite_complexes_list(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user.favorite_complexes.all(), many=True)
        return Response(serializer.data)

    @extend_schema(
        methods=["POST"],
        description="Get favourite complexes for a authenticated user. Permissions: IsAuthenticated",
    )
    @action(methods=["post"], detail=True, url_path="switch_complex_favorite")
    def switch_complex_favorite(self, request, *args, **kwargs):
        if self.get_object() in request.user.favorite_complexes.all():
            request.user.favorite_complexes.remove(self.get_object())
            return Response("Успешно удалён")
        request.user.favorite_complexes.add(self.get_object())
        return Response("Успешно добавлен")


@extend_schema(tags=["Photos"])
class PhotoViewSet(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = PhotoSerializer
    queryset = Photo.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'get', 'patch', 'delete']


@extend_schema(tags=["Files"])
class FileViewSet(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = FileSerializer
    queryset = File.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'get', 'patch', 'delete']


@extend_schema(tags=["Corp"])
class CorpViewSet(viewsets.ModelViewSet):
    serializer_class = CorpSerializer
    queryset = Corp.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'patch', 'delete']

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
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'post', 'delete']

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(complex=request.user.complex)
        return Response(serializer.data, status.HTTP_201_CREATED)


@extend_schema(tags=["Apartments"])
@extend_schema(
    methods=["GET"], description="Get all apartment. Permissions: IsAuthenticated"
)
@extend_schema(methods=["PUT", "PATCH"], description="Update specific apartment.")
@extend_schema(methods=["POST"], description="Create new apartment.")
class ApartmentViewSet(viewsets.ModelViewSet):
    serializer_class = ApartmentSerializer
    queryset = Apartment.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)

    @action(methods=['get'], detail=False, url_path="in_chessboard/(?P<floor_id>[^/.]+)/(?P<sewer_id>[^/.]+)",
            url_name="chessboard")
    def in_chessboard(self, request, floor_id, sewer_id, *args, **kwargs):
        try:
            apartment = Apartment.objects.get(floor_id=self.kwargs['floor_id'], sewer_id=self.kwargs['sewer_id'])
        except Apartment.DoesNotExist:
            return Response('Апартаменты отсутствуют в системе')
        serializer = self.serializer_class(apartment)
        return Response(data=serializer.data)


@extend_schema(tags=["Chessboards"])
@extend_schema(
    methods=["GET"], description="Get all apartment. Permissions: IsAuthenticated"
)
@extend_schema(methods=["PUT", "PATCH"], description="Update specific apartment.")
@extend_schema(methods=["POST"], description="Create new apartment.")
class ChessboardViewSet(viewsets.ModelViewSet):
    serializer_class = ChessBoardSerializer
    queryset = Complex.objects.all()

    permission_classes = [IsAuthenticated]

    @action(methods=['get'], detail=False, url_path="chessboards_for_my_complex", url_name="chessboards_for_my_complex")
    def chessboards_for_my_complex(self, request, *args, **kwargs):
        complex = Complex.objects.prefetch_related('corps').get(builder=request.user)
        result = {}
        for i, corp in enumerate(complex.corps.prefetch_related('sections').all()):
            # print(list(corp.sections.values().all()))
            if i == 0:
                result = corp.sections.all()
            result = result.union(corp.sections.all())
        print(result)
        serializer = self.serializer_class(result, many=True)

        return Response(data=serializer.data)
