from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import CompanyInfo
from .serializers import CompanyInfoSerializer


class CompanyInfoView(generics.RetrieveUpdateAPIView):
    """
    Информация о компании — singleton endpoint.

    GET   /api/v1/company/  — получить данные (публично)
    PUT   /api/v1/company/  — обновить данные (только admin)
    PATCH /api/v1/company/  — частично обновить (только admin)
    """
    serializer_class = CompanyInfoSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_object(self):
        return CompanyInfo.load()
