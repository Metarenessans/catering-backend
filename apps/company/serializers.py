from rest_framework import serializers
from .models import CompanyInfo, FooterNavigation, LegalDocument, PrivacyPolicy


class CompanyInfoSerializer(serializers.ModelSerializer):
    # ... existing fields ...
    class Meta:
        model = CompanyInfo
        fields = [
            "id",
            "company_name",
            "legal_name",
            "city",
            "address",
            "latitude",
            "longitude",
            "price_range",
            "serves_cuisine",
            "inn",
            "ogrn",
            "phone_number",
            "email",
            "telegram",
            "max_messenger",
            "vk",
            "reviews_url",
            "min_order_amount",
            "free_delivery_threshold",
            "delivery_cost",
            "hero_image_top",
            "hero_image_top_mobile",
            "hero_image_bottom",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class FooterNavigationSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="category.id")
    name = serializers.ReadOnlyField(source="category.name")
    category_slug = serializers.ReadOnlyField(source="category.slug")

    class Meta:
        model = FooterNavigation
        fields = ["id", "name", "category_slug", "order"]


class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = ["id", "title", "content_html", "updated_at"]
        read_only_fields = ["id", "updated_at"]


class LegalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalDocument
        fields = ["id", "slug", "title", "content_html", "order", "updated_at"]
        read_only_fields = ["id", "updated_at"]


