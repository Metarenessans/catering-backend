from rest_framework import serializers
from .models import Order, OrderItem


DELIVERY_THRESHOLD = 10000
DELIVERY_COST = 1500
MIN_ORDER = 5000


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_image_url",
            "price",
            "quantity",
            "subtotal",
        ]
        read_only_fields = ["id", "subtotal"]


class OrderItemCreateSerializer(serializers.Serializer):
    """
    Входной формат позиции из frontend-корзины.
    Принимает структуру CartItem: { name, imageUrl, priceInfo: { price }, quantity }
    """
    name = serializers.CharField()
    imageUrl = serializers.URLField(allow_blank=True, default="")
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField(min_value=1, max_value=999)
    product_id = serializers.IntegerField(required=False, allow_null=True)


class OrderCreateSerializer(serializers.Serializer):
    """
    Создание заказа из данных, которые frontend передаёт в onSubmit:
    { items: CartItem[], totalPrice, finalPrice }
    """
    items = OrderItemCreateSerializer(many=True)
    comment = serializers.CharField(allow_blank=True, default="", required=False)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Корзина не может быть пустой.")
        return items

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        comment = validated_data.get("comment", "")

        # Рассчитываем суммы на backend — не доверяем данным frontend
        total_price = sum(
            item["price"] * item["quantity"] for item in items_data
        )
        if total_price < MIN_ORDER:
            raise serializers.ValidationError(
                f"Минимальная сумма заказа — {MIN_ORDER} ₽."
            )

        delivery_cost = 0 if total_price >= DELIVERY_THRESHOLD else DELIVERY_COST
        final_price = total_price + delivery_cost

        order = Order.objects.create(
            total_price=total_price,
            delivery_cost=delivery_cost,
            final_price=final_price,
            comment=comment,
        )

        from ..catalog.models import Product

        for item in items_data:
            product_ref = None
            if item.get("product_id"):
                product_ref = Product.objects.filter(pk=item["product_id"]).first()

            OrderItem.objects.create(
                order=order,
                product=product_ref,
                product_name=item["name"],
                product_image_url=item.get("imageUrl", ""),
                price=item["price"],
                quantity=item["quantity"],
            )

        return order


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "total_price",
            "delivery_cost",
            "final_price",
            "comment",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]
