from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status

from builder.serializers import *


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
        print(self.get_object().id)
        print(request.user.favorite_complexes.all())
        if self.get_object() in request.user.favorite_complexes.all():
            request.user.favorite_complexes.remove(self.get_object())
            return Response("Успешно удалён")
        request.user.favorite_complexes.add(self.get_object())
        return Response("Успешно добавлен")


@extend_schema(tags=["Galleries"])
class GalleryViewSet(viewsets.ModelViewSet):
    serializer_class = GallerySerializer
    queryset = Gallery.objects.all()
    permission_classes = [IsAuthenticated]


@extend_schema(tags=["Photos"])
class PhotoViewSet(viewsets.ModelViewSet):
    serializer_class = PhotoSerializer
    queryset = Photo.objects.all()
    permission_classes = [IsAuthenticated]


@extend_schema(tags=["Corp"])
class CorpViewSet(viewsets.ModelViewSet):
    serializer_class = CorpSerializer
    queryset = Corp.objects.all()
    permission_classes = [IsAuthenticated]


@extend_schema(tags=["Floors"])
class FloorViewSet(viewsets.ModelViewSet):
    serializer_class = FloorSerializer
    queryset = Floor.objects.all()
    permission_classes = [IsAuthenticated]


@extend_schema(tags=["Sections"])
class SectionViewSet(viewsets.ModelViewSet):
    serializer_class = SectionSerializer
    queryset = Section.objects.all()
    permission_classes = [IsAuthenticated]


@extend_schema(tags=["Sewers"])
class SewerViewSet(viewsets.ModelViewSet):
    serializer_class = SewerSerializer
    queryset = Sewer.objects.all()
    permission_classes = [IsAuthenticated]


@extend_schema(tags=["Flats"])
@extend_schema(
    methods=["GET"], description="Get all flats. Permissions: IsAuthenticated"
)
@extend_schema(methods=["PUT", "PATCH"], description="Update specific flat.")
@extend_schema(methods=["POST"], description="Create new flat.")
class FlatViewSet(viewsets.ModelViewSet):
    serializer_class = FlatSerializer
    queryset = Flat.objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        description="Get flats for a specific section in specific complex.",
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="sort_by_complex/(?P<complex_id>[^/.]+)",
    )
    def sort_by_complex(self, request, complex_id=None):
        news = self.queryset.filter(complex_id=complex_id)
        serializer = self.serializer_class(news, many=True)
        return Response(serializer.data)


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
