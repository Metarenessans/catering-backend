from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Order, OrderItem, TelegramSubscriber, EmailSubscriber
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/send-telegram/',
                self.admin_site.admin_view(self.send_telegram_view),
                name='order-send-telegram',
            ),
            path(
                '<path:object_id>/send-email/',
                self.admin_site.admin_view(self.send_email_view),
                name='order-send-email',
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

    def send_email_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj:
            try:
                from .email import send_order_email_notification_sync
                send_order_email_notification_sync(obj.id, raise_exception=True)
                self.message_user(request, "Уведомление на почту успешно отправлено!", messages.SUCCESS)
            except Exception as e:
                self.message_user(request, f"Ошибка при отправке: {e}", messages.ERROR)
        return HttpResponseRedirect("../change/")

    @admin.display(description="Отправка уведомлений")
    def send_telegram_button(self, obj):
        if obj and obj.pk:
            tg_url = reverse('admin:order-send-telegram', args=[obj.pk])
            email_url = reverse('admin:order-send-email', args=[obj.pk])
            return mark_safe(
                f'<a class="button" href="{tg_url}" style="background-color: #007bff; color: white; padding: 8px 12px; border-radius: 4px; font-weight: bold; text-decoration: none; display: inline-block; margin-right: 10px;">'
                f'Отправить в Telegram'
                f'</a>'
                f'<a class="button" href="{email_url}" style="background-color: #28a745; color: white; padding: 8px 12px; border-radius: 4px; font-weight: bold; text-decoration: none; display: inline-block;">'
                f'Отправить на почту'
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

@admin.register(EmailSubscriber)
class EmailSubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["email", "name"]
    list_editable = ["is_active"]
    readonly_fields = ["created_at", "updated_at"]
    fields = ["email", "name", "is_active", "created_at", "updated_at"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "check-smtp/",
                self.admin_site.admin_view(self.check_smtp_view),
                name="emailsubscriber-check-smtp",
            ),
        ]
        return custom_urls + urls

    def check_smtp_view(self, request):
        import os
        from django.shortcuts import render
        from django.core.mail import send_mail
        from django.conf import settings
        import traceback

        # Get settings values (with masking of host password)
        email_host = getattr(settings, 'EMAIL_HOST', None) or os.getenv('EMAIL_HOST')
        email_port = getattr(settings, 'EMAIL_PORT', None) or os.getenv('EMAIL_PORT')
        email_use_ssl = getattr(settings, 'EMAIL_USE_SSL', None)
        email_use_tls = getattr(settings, 'EMAIL_USE_TLS', None)
        email_host_user = getattr(settings, 'EMAIL_HOST_USER', None) or os.getenv('EMAIL_HOST_USER')
        email_host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', None) or os.getenv('EMAIL_HOST_PASSWORD')
        default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or os.getenv('DEFAULT_FROM_EMAIL')

        masked_password = "— (Не задан)"
        if email_host_password:
            masked_password = f"Задан (длина: {len(email_host_password)})"
            if len(email_host_password) > 4:
                masked_password += f" [начинается на '{email_host_password[:2]}...', заканчивается на '...{email_host_password[-2:]}']"

        settings_info = {
            "EMAIL_HOST": email_host or "— (Пусто)",
            "EMAIL_PORT": str(email_port) if email_port is not None else "— (Пусто)",
            "EMAIL_USE_SSL": str(email_use_ssl),
            "EMAIL_USE_TLS": str(email_use_tls),
            "EMAIL_HOST_USER": email_host_user or "— (Пусто)",
            "EMAIL_HOST_PASSWORD": masked_password,
            "DEFAULT_FROM_EMAIL": default_from_email or "— (Пусто)",
        }

        # Check active subscribers in database
        active_subs = list(self.model.objects.filter(is_active=True))
        subscribers_info = {
            "count": len(active_subs),
            "emails": [sub.email for sub in active_subs],
        }

        test_status = None
        test_error = None
        test_email = request.POST.get("test_email") if request.method == "POST" else None

        if request.method == "POST" and test_email:
            try:
                from_email = default_from_email or email_host_user
                send_mail(
                    subject="Тестовое сообщение SMTP ChefMil",
                    message="Если вы получили это письмо, настройки SMTP настроены и работают корректно!",
                    from_email=from_email,
                    recipient_list=[test_email],
                    fail_silently=False,
                    html_message="<h2>Проверка связи SMTP</h2><p>Если вы получили это письмо, настройки SMTP настроены и работают корректно!</p>"
                )
                test_status = "success"
            except Exception:
                test_status = "error"
                test_error = traceback.format_exc()

        context = {
            **self.admin_site.each_context(request),
            "title": "Диагностика и проверка SMTP",
            "settings_info": settings_info,
            "subscribers_info": subscribers_info,
            "test_email": test_email or request.user.email or "",
            "test_status": test_status,
            "test_error": test_error,
        }

        return render(request, "admin/orders/emailsubscriber/check_smtp.html", context)
