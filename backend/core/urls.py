from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CompetitionCategoryViewSet,
    CompetitionViewSet,
    HealthAPIView,
    PlayerViewSet,
)


router = DefaultRouter()

router.register(r"players", PlayerViewSet, basename="player")

router.register(
    r"competitions",
    CompetitionViewSet,
    basename="competition"
)

router.register(
    r"categories",
    CategoryViewSet,
    basename="category"
)

router.register(
    r"competition-categories",
    CompetitionCategoryViewSet,
    basename="competition-category",
)

urlpatterns = [
    path("health/", HealthAPIView.as_view(), name="health"),
    path("", include(router.urls)),
]