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


class PriceInfoSerializer(serializers.Serializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2)


class OrderItemCreateSerializer(serializers.Serializer):
    """
    Входной формат позиции из frontend-корзины.
    Принимает структуру CartItem: { name, imageUrl, priceInfo: { price }, quantity }
    """
    name = serializers.CharField()
    imageUrl = serializers.URLField(allow_blank=True, default="")
    priceInfo = PriceInfoSerializer()
    quantity = serializers.IntegerField(min_value=1, max_value=999)
    id = serializers.CharField(required=False, allow_null=True)
    productId = serializers.IntegerField(required=False, allow_null=True)


class OrderCreateSerializer(serializers.Serializer):
    """
    Создание заказа из данных, которые frontend передаёт в onSubmit:
    { items: CartItem[], totalPrice, finalPrice, name, phone, contact_method }
    """
    items = OrderItemCreateSerializer(many=True)
    name = serializers.CharField(max_length=200, required=True)
    phone = serializers.CharField(max_length=30, required=True)
    contact_method = serializers.CharField(max_length=50, default="Позвонить мне", required=False)
    comment = serializers.CharField(allow_blank=True, default="", required=False)
    cart_link = serializers.URLField(allow_blank=True, default="", required=False)
    guests = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    event_date = serializers.DateField(required=False, allow_null=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Корзина не может быть пустой.")
        return items

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        comment = validated_data.get("comment", "")
        cart_link = validated_data.get("cart_link", "")
        name = validated_data.get("name", "")
        phone = validated_data.get("phone", "")
        contact_method = validated_data.get("contact_method", "Позвонить мне")
        guests = validated_data.get("guests", "")
        event_date = validated_data.get("event_date")

        # Рассчитываем суммы на backend — не доверяем данным frontend
        total_price = sum(
            item["priceInfo"]["price"] * item["quantity"] for item in items_data
        )
        if total_price < MIN_ORDER:
            raise serializers.ValidationError(
                f"Минимальная сумма заказа — {MIN_ORDER} ₽."
            )

        delivery_cost = 0 if total_price >= DELIVERY_THRESHOLD else DELIVERY_COST
        final_price = total_price + delivery_cost

        order = Order.objects.create(
            name=name,
            phone=phone,
            contact_method=contact_method,
            guests=guests,
            event_date=event_date,
            total_price=total_price,
            delivery_cost=delivery_cost,
            final_price=final_price,
            comment=comment,
            cart_link=cart_link,
        )

        from ..catalog.models import Product

        for item in items_data:
            product_ref = None
            # Проверяем и productId, и id (на случай если frontend передаст базу в id)
            p_id = item.get("productId") or item.get("id")
            if p_id and str(p_id).isdigit():
                product_ref = Product.objects.filter(pk=int(p_id)).first()

            OrderItem.objects.create(
                order=order,
                product=product_ref,
                product_name=item["name"],
                product_image_url=item.get("imageUrl", ""),
                price=item["priceInfo"]["price"],
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
            "name",
            "phone",
            "contact_method",
            "guests",
            "event_date",
            "total_price",
            "delivery_cost",
            "final_price",
            "comment",
            "cart_link",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]
