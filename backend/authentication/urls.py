from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrganizerViewSet


router = DefaultRouter()
router.register(r"organizers", OrganizerViewSet, basename="organizer")

urlpatterns = [
    path("", include(router.urls)),
]
