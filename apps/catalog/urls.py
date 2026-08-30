from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import SectionViewSet, CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register(r"sections", SectionViewSet, basename="section")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
]
