from rest_framework import serializers
from .models import Category, Product, ProductExtraInfo, ProductOption


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
        fields = ["id", "amount", "unit", "is_active", "order"]


class ProductOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOption
        fields = ["id", "name", "price", "old_price", "min_order_quantity", "is_active", "order"]


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор продукта.
    Формат ответа максимально близок к структуре, используемой во frontend.
    """
    extra_info = ProductExtraInfoSerializer(many=True, read_only=True)
    options = ProductOptionSerializer(many=True, read_only=True)
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
            "min_order_quantity",
            "extra_info",
            "options",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "effective_image_url"]

    def to_representation(self, instance):
        # FAST PATH: Read directly from the model instance instead of DRF's slow ModelSerializer loop
        request = self.context.get("request")
        
        # 1. Resolve image URL directly
        url = instance.effective_image_url
        if url and not (url.startswith("http://") or url.startswith("https://")):
            if request and url.startswith("/"):
                url = request.build_absolute_uri(url)
                
        # 2. Extract nested info directly from prefetched relations (no extra SQL queries due to prefetch_related)
        extra_info_list = [
            {"amount": float(info.amount), "unit": info.unit}
            for info in instance.extra_info.all()
            if info.is_active
        ]
        
        options_list = [
            {
                "id": str(opt.id),
                "name": opt.name,
                "price": float(opt.price),
                "oldPrice": float(opt.old_price) if opt.old_price is not None else None,
                "minOrderQuantity": opt.min_order_quantity if opt.min_order_quantity is not None else instance.min_order_quantity,
            }
            for opt in instance.options.all()
            if opt.is_active
        ]
        
        # 3. Build response dictionary instantly
        return {
            "id": str(instance.id),
            "name": instance.name,
            "categoryId": instance.category.slug if instance.category_id else None,
            "imageUrl": url,
            "description": instance.description or "",
            "priceInfo": {
                "price": float(instance.price) if instance.price is not None else 0,
                "oldPrice": float(instance.old_price) if instance.old_price is not None else None,
            },
            "extraInfo": extra_info_list,
            "options": options_list,
            "minOrderQuantity": instance.min_order_quantity
        }


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
            "min_order_quantity",
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
