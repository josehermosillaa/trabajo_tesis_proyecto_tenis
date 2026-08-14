from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CompetitionCategoryViewSet,
    CompetitionViewSet,
    HealthAPIView,
    PlayerViewSet,
    RegistrationViewSet,
    CourtViewSet,
    MatchViewSet,
    MatchSetViewSet,
    StandingViewSet
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

router.register(
    r"registrations",
    RegistrationViewSet,
    basename="registration",
)
router.register(
    r"courts",
    CourtViewSet,
    basename="court",
)

router.register(
    r"matches",
    MatchViewSet,
    basename="match",
)

router.register(
    r"match-sets",
    MatchSetViewSet,
    basename="match-set",
)

router.register(
    r"standings",
    StandingViewSet,
    basename="standing",
)

urlpatterns = [
    path("health/", HealthAPIView.as_view(), name="health"),
    path("", include(router.urls)),
]


