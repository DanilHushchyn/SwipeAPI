from rest_framework.routers import DefaultRouter

from admin.views import NotaryViewSet

router = DefaultRouter()
router.register(r"notaries", NotaryViewSet, basename="notary")
urlpatterns = router.urls
