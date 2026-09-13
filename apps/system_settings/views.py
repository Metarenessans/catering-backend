from rest_framework import generics, permissions
from .models import SystemSettings, SeoSettings
from .serializers import SystemSettingsSerializer, SeoSettingsSerializer


class SystemSettingsView(generics.RetrieveAPIView):
    """
    Возвращает публичные системные настройки.
    """
    serializer_class = SystemSettingsSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return SystemSettings.load()


class SeoSettingsView(generics.RetrieveAPIView):
    """
    Возвращает настройки SEO (Singleton).
    """
    serializer_class = SeoSettingsSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return SeoSettings.load()
