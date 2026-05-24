from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Order, OrderItem, TelegramSubscriber




class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["image_preview", "product", "product_name", "price", "quantity", "subtotal"]
    can_delete = False

    def image_preview(self, obj):
        url = obj.product_image_url
        if url:
            return mark_safe(
                f'<img src="{url}" width="100" style="border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />'
            )
        return "Нет фото"

    image_preview.short_description = "Предпросмотр"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "status",
        "name",
        "phone",
        "guests",
        "event_date",
        "total_price",
        "delivery_cost",
        "final_price",
        "items_count",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["id", "comment"]
    ordering = ["-created_at"]
    readonly_fields = ["total_price", "delivery_cost", "final_price", "cart_link_clickable", "created_at", "updated_at"]
    fields = [
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
        "cart_link_clickable",
        "created_at",
        "updated_at",
    ]
    list_editable = ["status"]
    inlines = [OrderItemInline]

    @admin.display(description="Позиций")
    def items_count(self, obj):
        return obj.items.count()

    @admin.display(description="Ссылка на корзину")
    def cart_link_clickable(self, obj):
        if obj.cart_link:
            return mark_safe(
                f'<a href="{obj.cart_link}" target="_blank" style="color: #007bff; text-decoration: underline; word-break: break-all;">'
                f'{obj.cart_link}</a>'
            )
        return "Нет ссылки"


@admin.register(TelegramSubscriber)
class TelegramSubscriberAdmin(admin.ModelAdmin):
    list_display = ["username", "phone", "chat_id", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["username", "phone", "chat_id"]
    list_editable = ["is_active"]
    readonly_fields = ["chat_id", "created_at", "updated_at"]
    fields = ["username", "phone", "chat_id", "is_active", "created_at", "updated_at"]


