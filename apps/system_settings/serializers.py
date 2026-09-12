from rest_framework import serializers
from .models import SystemSettings


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = ["sitemap_cache_minutes", "enable_debug_json_file", "updated_at"]
