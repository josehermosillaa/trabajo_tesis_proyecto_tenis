from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    HealthAPIView, 
    PlayerViewSet, 
    CompetitionViewSet,
    CategoryViewSet,
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

urlpatterns = [
    path("health/", HealthAPIView.as_view(), name="health"),
    path("", include(router.urls)),
]