from rest_framework.routers import DefaultRouter

from builder.views import *

router = DefaultRouter()
router.register(
    prefix=r"complexes", viewset=ComplexViewSet, basename="complexes"
)
router.register(prefix=r"apartment", viewset=ApartmentViewSet, basename="apartment")
router.register(prefix=r"chessboards", viewset=ChessboardViewSet, basename="chessboards")

# router.register(
#     prefix=r"galleries", viewset=GalleryViewSet, basename="galleries"
# )
router.register(prefix=r"photos", viewset=PhotoViewSet, basename="photos")
router.register(prefix=r"files", viewset=FileViewSet, basename="files")
router.register(prefix=r"corps", viewset=CorpViewSet, basename="corps")
# router.register(
#     prefix=r"sections", viewset=SectionViewSet, basename="sections"
# )
# router.register(prefix=r"floors", viewset=FloorViewSet, basename="floors")
# router.register(prefix=r"sewers", viewset=SewerViewSet, basename="sewers")
router.register(prefix=r"news", viewset=NewsViewSet, basename="news")
urlpatterns = router.urls
