from rest_framework import serializers
from .models import Category, Product, ProductExtraInfo


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "name", "order", "is_active"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Frontend expects `id` to be the slug
        ret["id"] = ret.pop("slug", "")
        return ret


class ProductExtraInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductExtraInfo
        fields = ["id", "amount", "unit", "order"]


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор продукта.
    Формат ответа максимально близок к структуре, используемой во frontend.
    """
    extra_info = ProductExtraInfoSerializer(many=True, read_only=True)
    category_slug = serializers.SlugRelatedField(
        source="category",
        slug_field="slug",
        queryset=Category.objects.all(),
        required=False,
        allow_null=True,
    )
    effective_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "category",
            "category_slug",
            "image_url",
            "image",
            "effective_image_url",
            "description",
            "price",
            "old_price",
            "is_active",
            "is_featured",
            "order",
            "extra_info",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "effective_image_url"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Format matching frontend ProductData exactly
        return {
            "id": str(ret.get("id")),
            "name": ret.get("name"),
            "categoryId": ret.get("category_slug"),
            "imageUrl": ret.get("effective_image_url"),
            "description": ret.get("description", ""),
            "priceInfo": {
                "price": float(ret["price"]) if ret.get("price") else 0,
                "oldPrice": float(ret["old_price"]) if ret.get("old_price") else None,
            },
            "extraInfo": [
                {
                    "amount": float(info["amount"]),
                    "unit": info["unit"]
                }
                for info in ret.get("extra_info", [])
            ]
        }

    def get_effective_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            url = obj.image.url
            return request.build_absolute_uri(url) if request else url
        return obj.image_url


class ProductWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания/обновления продукта с вложенными extra_info.
    """
    extra_info = ProductExtraInfoSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "category",
            "image_url",
            "image",
            "description",
            "price",
            "old_price",
            "is_active",
            "is_featured",
            "order",
            "extra_info",
        ]

    def create(self, validated_data):
        extra_info_data = validated_data.pop("extra_info", [])
        product = Product.objects.create(**validated_data)
        for info in extra_info_data:
            ProductExtraInfo.objects.create(product=product, **info)
        return product

    def update(self, instance, validated_data):
        extra_info_data = validated_data.pop("extra_info", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if extra_info_data is not None:
            instance.extra_info.all().delete()
            for info in extra_info_data:
                ProductExtraInfo.objects.create(product=instance, **info)

        return instance
