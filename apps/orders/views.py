from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import Order
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer,
)
from .filters import OrderFilter


class OrderViewSet(viewsets.ModelViewSet):
    """
    Управление заказами.

    POST   /api/v1/orders/        — создать заказ из корзины (публично)
    GET    /api/v1/orders/        — список всех заказов (только admin)
    GET    /api/v1/orders/{id}/   — детали заказа (только admin)
    PATCH  /api/v1/orders/{id}/status/ — изменить статус (только admin)
    DELETE /api/v1/orders/{id}/   — удалить (только admin)
    """
    queryset = Order.objects.prefetch_related("items").all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ["created_at", "final_price", "status"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        if self.action == "update_status":
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        response_serializer = OrderSerializer(order, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        """Обновить статус заказа."""
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data)
