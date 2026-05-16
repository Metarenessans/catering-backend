from rest_framework import serializers
from .models import CompanyInfo, FooterNavigation


class CompanyInfoSerializer(serializers.ModelSerializer):
    # ... existing fields ...
    class Meta:
        model = CompanyInfo
        fields = [
            "id",
            "company_name",
            "address",
            "inn",
            "ogrn",
            "phone_number",
            "email",
            "telegram",
            "max_messenger",
            "reviews_url",
            "min_order_amount",
            "free_delivery_threshold",
            "delivery_cost",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class FooterNavigationSerializer(serializers.ModelSerializer):
    category_slug = serializers.ReadOnlyField(source="category.slug")

    class Meta:
        model = FooterNavigation
        fields = ["id", "name", "category_slug", "order"]
