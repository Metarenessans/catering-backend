from rest_framework import serializers
from .models import SystemSettings, SeoSettings


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = ["sitemap_cache_minutes", "enable_debug_json_file", "updated_at"]


class SeoSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeoSettings
        fields = [
            "home_title",
            "home_description",
            "blog_title",
            "blog_description",
            "updated_at",
        ]
