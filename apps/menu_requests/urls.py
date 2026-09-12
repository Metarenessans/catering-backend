from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import MenuRequestViewSet, AdditionalServiceViewSet, EventFormatViewSet, CalculatePageSettingsView

router = DefaultRouter()
router.register(r"services", AdditionalServiceViewSet, basename="additional-service")
router.register(r"formats", EventFormatViewSet, basename="event-format")
router.register(r"", MenuRequestViewSet, basename="menu-request")

urlpatterns = [
    path("calculate-settings/", CalculatePageSettingsView.as_view(), name="calculate-settings"),
    path("", include(router.urls)),
]
