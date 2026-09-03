from rest_framework import generics, permissions
from .models import SystemSettings
from .serializers import SystemSettingsSerializer


class SystemSettingsView(generics.RetrieveAPIView):
    """
    Возвращает публичные системные настройки.
    """
    serializer_class = SystemSettingsSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return SystemSettings.load()
