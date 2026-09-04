from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from django.db.models import Q, Prefetch
from .models import Section, Category, Product, SectionCategory
from .serializers import (
    SectionSerializer,
    CategorySerializer,
    ProductSerializer,
    ProductWriteSerializer,
)
from .filters import ProductFilter


class SectionViewSet(viewsets.ModelViewSet):
    """
    CRUD для разделов продуктов.

    list:   GET  /api/v1/catalog/sections/
    create: POST /api/v1/catalog/sections/
    retrieve: GET /api/v1/catalog/sections/{id}/
    update: PUT  /api/v1/catalog/sections/{id}/
    destroy: DELETE /api/v1/catalog/sections/{id}/
    """
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    pagination_class = None
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "slug"]
    ordering_fields = ["order", "name"]
    ordering = ["order"]

    def get_queryset(self):
        qs = Section.objects.prefetch_related(
            Prefetch(
                "section_categories",
                queryset=SectionCategory.objects.select_related("category").filter(category__is_active=True).order_by("order", "id")
            )
        ).all()
        # Admins see all sections; public only sees active ones
        if self.request.user and self.request.user.is_staff:
            return qs
        return qs.filter(is_active=True)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD для категорий продуктов.

    list:   GET  /api/v1/catalog/categories/
    create: POST /api/v1/catalog/categories/
    retrieve: GET /api/v1/catalog/categories/{id}/
    update: PUT  /api/v1/catalog/categories/{id}/
    destroy: DELETE /api/v1/catalog/categories/{id}/
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["sections", "sections__slug"]
    search_fields = ["name", "slug"]
    ordering_fields = ["order", "name"]
    ordering = ["order"]

    def get_queryset(self):
        qs = Category.objects.prefetch_related("sections").all()
        # Admins see all categories; public only sees active ones
        if self.request.user and self.request.user.is_staff:
            return qs
        return qs.filter(is_active=True)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD для продуктов каталога.

    list:     GET  /api/v1/catalog/products/
    create:   POST /api/v1/catalog/products/
    retrieve: GET  /api/v1/catalog/products/{id}/
    update:   PUT  /api/v1/catalog/products/{id}/
    destroy:  DELETE /api/v1/catalog/products/{id}/
    featured: GET  /api/v1/catalog/products/featured/
    """
    queryset = (
        Product.objects.select_related("category")
        .prefetch_related("extra_info")
        .filter(is_active=True)
    )
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "category__name"]
    ordering_fields = ["price", "name", "order", "created_at"]
    ordering = ["order", "name"]

    def get_queryset(self):
        qs = Product.objects.select_related("category").prefetch_related("extra_info", "options")
        # Admins see all products; public only sees active ones
        if self.request.user and self.request.user.is_staff:
            return qs
        return qs.filter(is_active=True).filter(Q(category__is_active=True) | Q(category__isnull=True))

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProductWriteSerializer
        return ProductSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "featured"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @action(detail=False, methods=["get"], url_path="featured")
    def featured(self, request):
        """Возвращает список рекомендуемых (выгодных) продуктов."""
        qs = self.get_queryset().filter(is_featured=True)
        serializer = ProductSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)
