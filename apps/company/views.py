from rest_framework import generics, permissions
from .models import CompanyInfo, FooterNavigation, LegalDocument, PrivacyPolicy
from .serializers import (
    CompanyInfoSerializer,
    FooterNavigationSerializer,
    LegalDocumentSerializer,
    PrivacyPolicySerializer,
)


class CompanyInfoView(generics.RetrieveUpdateAPIView):
    # ... existing code ...
    serializer_class = CompanyInfoSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_object(self):
        return CompanyInfo.load()


class FooterNavigationListView(generics.ListAPIView):
    """
    Список элементов навигации в футере.
    """
    queryset = FooterNavigation.objects.all()
    serializer_class = FooterNavigationSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # Отключаем пагинацию для этого списка


class LegalDocumentListView(generics.ListAPIView):
    """
    Список всех правовых документов компании.
    """
    queryset = LegalDocument.objects.all()
    serializer_class = LegalDocumentSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class LegalDocumentDetailView(generics.RetrieveUpdateAPIView):
    """
    Получение конкретного правового документа по slug.
    GET доступен всем, PUT/PATCH — только администраторам.
    """
    queryset = LegalDocument.objects.all()
    serializer_class = LegalDocumentSerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_object(self):
        slug = self.kwargs.get("slug")
        return LegalDocument.get_document(slug)


class PrivacyPolicyView(generics.RetrieveUpdateAPIView):
    """
    Получение и обновление политики конфиденциальности.
    GET доступен всем (публично), PUT/PATCH — только администраторам.
    """
    serializer_class = LegalDocumentSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_object(self):
        return LegalDocument.get_document("privacy-policy")


