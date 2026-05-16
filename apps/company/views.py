from rest_framework import generics, permissions
from .models import CompanyInfo, FooterNavigation
from .serializers import CompanyInfoSerializer, FooterNavigationSerializer


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
