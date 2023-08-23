from rest_framework.routers import DefaultRouter

from client.views import *

router = DefaultRouter()
router.register(prefix=r"announcements", viewset=AnnouncementViewSet, basename="announcements")
router.register(prefix=r"complaints", viewset=ComplaintViewSet, basename="complaints")
router.register(
    prefix=r"subscriptions",
    viewset=SubscriptionViewSet,
    basename="subscriptions",
)
router.register(
    prefix=r"promotions", viewset=PromotionViewSet, basename="promotions"
)
router.register(prefix=r"filters", viewset=FilterViewSet, basename="filters")
router.register(prefix=r"chats", viewset=ChatViewSet, basename="chats")
router.register(
    prefix=r"messages", viewset=MessageViewSet, basename="messages"
)
urlpatterns = router.urls
