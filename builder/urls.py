from rest_framework.routers import DefaultRouter

from builder.views import *

router = DefaultRouter()
router.register(
    prefix=r"complexes", viewset=ComplexViewSet, basename="complexes"
)
router.register(prefix=r"apartments", viewset=ApartmentViewSet, basename="apartments")
router.register(prefix=r"chessboards", viewset=ChessboardViewSet, basename="chessboards")
router.register(prefix=r"photos", viewset=PhotoViewSet, basename="photos")
router.register(prefix=r"files", viewset=FileViewSet, basename="files")
router.register(prefix=r"corps", viewset=CorpViewSet, basename="corps")
router.register(prefix=r"news", viewset=NewsViewSet, basename="news")
urlpatterns = router.urls
