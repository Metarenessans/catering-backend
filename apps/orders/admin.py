from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Order, OrderItem


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
        "total_price",
        "delivery_cost",
        "final_price",
        "items_count",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["id", "comment"]
    ordering = ["-created_at"]
    readonly_fields = ["total_price", "delivery_cost", "final_price", "created_at", "updated_at"]
    list_editable = ["status"]
    inlines = [OrderItemInline]

    @admin.display(description="Позиций")
    def items_count(self, obj):
        return obj.items.count()
