from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import MenuRequest, AdditionalService, EventFormat
from .serializers import (
    MenuRequestSerializer,
    MenuRequestCreateSerializer,
    MenuRequestStatusUpdateSerializer,
    AdditionalServiceSerializer,
    EventFormatSerializer,
)
from .filters import MenuRequestFilter


class MenuRequestViewSet(viewsets.ModelViewSet):
    """
    Управление заявками на подбор меню.

    POST  /api/v1/menu-requests/            — создать заявку (публично)
    GET   /api/v1/menu-requests/            — список заявок (только admin)
    GET   /api/v1/menu-requests/{id}/       — детали заявки (только admin)
    PATCH /api/v1/menu-requests/{id}/status/ — изменить статус (только admin)
    """
    queryset = MenuRequest.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MenuRequestFilter
    search_fields = ["name", "phone", "format"]
    ordering_fields = ["created_at", "date", "guests", "status"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return MenuRequestCreateSerializer
        if self.action == "update_status":
            return MenuRequestStatusUpdateSerializer
        return MenuRequestSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def create(self, request, *args, **kwargs):
        serializer = MenuRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        menu_request = serializer.save()
        response_serializer = MenuRequestSerializer(menu_request)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        """Обновить статус/заметки заявки."""
        obj = self.get_object()
        serializer = MenuRequestStatusUpdateSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(MenuRequestSerializer(obj).data)


class AdditionalServiceViewSet(viewsets.ModelViewSet):
    """
    CRUD для дополнительных услуг (Выездное накрытие, Официанты и т.д.)
    """
    queryset = AdditionalService.objects.all()
    serializer_class = AdditionalServiceSerializer
    pagination_class = None
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["label"]
    ordering = ["order"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class EventFormatViewSet(viewsets.ModelViewSet):
    """
    CRUD для форматов мероприятий (Юбилей, Свадьба, Фуршет и т.д.)
    """
    queryset = EventFormat.objects.filter(is_active=True)
    serializer_class = EventFormatSerializer
    pagination_class = None
    filter_backends = [OrderingFilter]
    ordering = ["order"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
