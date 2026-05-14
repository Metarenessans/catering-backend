from rest_framework import serializers
from .models import CompanyInfo


class CompanyInfoSerializer(serializers.ModelSerializer):
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
            "min_order_amount",
            "free_delivery_threshold",
            "delivery_cost",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]
