from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import FaqItem
from .serializers import FaqItemSerializer


class FaqItemViewSet(viewsets.ModelViewSet):
    """
    CRUD для вопросов FAQ.

    GET  /api/v1/faq/  — список вопросов (публично)
    POST /api/v1/faq/  — создать вопрос (только admin)
    """
    queryset = FaqItem.objects.filter(is_active=True)
    serializer_class = FaqItemSerializer
    pagination_class = None
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["question"]
    ordering_fields = ["order"]
    ordering = ["order"]

    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return FaqItem.objects.all()
        return FaqItem.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
