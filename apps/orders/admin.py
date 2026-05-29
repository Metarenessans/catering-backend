from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Order, OrderItem, TelegramSubscriber
from .telegram import send_order_telegram_notification


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
    readonly_fields = ["total_price", "delivery_cost", "final_price", "cart_link_clickable", "send_telegram_button", "created_at", "updated_at"]
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
        "send_telegram_button",
        "created_at",
        "updated_at",
    ]
    list_editable = ["status"]
    inlines = [OrderItemInline]

    class Media:
        css = {
            "all": ("admin/css/sortable_custom.css",)
        }

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/send-telegram/',
                self.admin_site.admin_view(self.send_telegram_view),
                name='order-send-telegram',
            ),
        ]
        return custom_urls + urls

    def send_telegram_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj:
            try:
                send_order_telegram_notification(obj)
                self.message_user(request, "Уведомление в Telegram успешно отправлено!", messages.SUCCESS)
            except Exception as e:
                self.message_user(request, f"Ошибка при отправке: {e}", messages.ERROR)
        return HttpResponseRedirect("../change/")

    @admin.display(description="Отправка уведомления")
    def send_telegram_button(self, obj):
        if obj and obj.pk:
            url = reverse('admin:order-send-telegram', args=[obj.pk])
            return mark_safe(
                f'<a class="button" href="{url}" style="background-color: #007bff; color: white; padding: 8px 12px; border-radius: 4px; font-weight: bold; text-decoration: none; display: inline-block;">'
                f'Отправить уведомление в Telegram'
                f'</a>'
            )
        return "Сначала сохраните объект"

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


