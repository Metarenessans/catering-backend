from django.contrib import admin
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django.contrib import messages
from adminsortable2.admin import SortableAdminMixin
from .models import MenuRequest, AdditionalService, EventFormat
from ..catalog.mixins import MakeFirstAdminMixin
from ..orders.telegram import send_menu_request_telegram_notification


@admin.register(MenuRequest)
class MenuRequestAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "phone",
        "contact_method",
        "format",
        "guests",
        "date",
        "status",
        "created_at",
    ]
    list_filter = ["status", "format", "date"]
    search_fields = ["name", "phone", "format"]
    ordering = ["-created_at"]
    readonly_fields = [
        "created_at",
        "updated_at",
        "food_preferences",
        "additional_services",
        "additional_services_display",
        "send_telegram_button",
    ]
    list_editable = ["status"]


    fieldsets = [
        (
            "Данные мероприятия",
            {
                "fields": ["format", "guests", "date", "food_preferences"],
            },
        ),
        (
            "Контактные данные",
            {
                "fields": ["name", "phone", "contact_method", "consent"],
            },
        ),
        (
            "Услуги",
            {
                "fields": ["additional_services_display"],
            },
        ),
        (
            "Статус и заметки",
            {
                "fields": ["status", "notes"],
            },
        ),
        (
            "Тестирование уведомлений",
            {
                "fields": ["send_telegram_button"],
            },
        ),
        (
            "Служебная информация",
            {
                "fields": ["created_at", "updated_at", "additional_services"],
                "classes": ["collapse"],
            },
        ),
    ]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/send-telegram/',
                self.admin_site.admin_view(self.send_telegram_view),
                name='menu-request-send-telegram',
            ),
            path(
                '<path:object_id>/send-email/',
                self.admin_site.admin_view(self.send_email_view),
                name='menu-request-send-email',
            ),
        ]
        return custom_urls + urls

    def send_telegram_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj:
            try:
                send_menu_request_telegram_notification(obj)
                self.message_user(request, "Уведомление в Telegram успешно отправлено!", messages.SUCCESS)
            except Exception as e:
                self.message_user(request, f"Ошибка при отправке: {e}", messages.ERROR)
        return HttpResponseRedirect("../change/")

    def send_email_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj:
            try:
                from ..orders.email import send_menu_request_email_notification
                send_menu_request_email_notification(obj)
                self.message_user(request, "Уведомление на почту успешно отправлено!", messages.SUCCESS)
            except Exception as e:
                self.message_user(request, f"Ошибка при отправке: {e}", messages.ERROR)
        return HttpResponseRedirect("../change/")

    @admin.display(description="Отправка уведомлений")
    def send_telegram_button(self, obj):
        if obj and obj.pk:
            tg_url = reverse('admin:menu-request-send-telegram', args=[obj.pk])
            email_url = reverse('admin:menu-request-send-email', args=[obj.pk])
            return mark_safe(
                f'<a class="button" href="{tg_url}" style="background-color: #007bff; color: white; padding: 8px 12px; border-radius: 4px; font-weight: bold; text-decoration: none; display: inline-block; margin-right: 10px;">'
                f'Отправить в Telegram'
                f'</a>'
                f'<a class="button" href="{email_url}" style="background-color: #28a745; color: white; padding: 8px 12px; border-radius: 4px; font-weight: bold; text-decoration: none; display: inline-block;">'
                f'Отправить на почту'
                f'</a>'
            )
        return "Сначала сохраните объект"

    def additional_services_display(self, obj):
        service_ids = obj.additional_services
        if not service_ids or not isinstance(service_ids, list):
            return "Нет выбранных услуг"

        # Get all services that exist in the database with their linked products
        services = AdditionalService.objects.filter(pk__in=service_ids).select_related('linked_product')
        services_dict = {str(service.id): service for service in services}

        html = ["<ul style='margin: 0; padding-left: 20px;'>"]
        for sid in service_ids:
            service = services_dict.get(str(sid))
            if service:
                # Link to the service admin change page
                try:
                    service_admin_url = reverse('admin:menu_requests_additionalservice_change', args=[service.id])
                    service_link = f'<a href="{service_admin_url}"><strong>{service.label}</strong></a>'
                except Exception:
                    service_link = f'<strong>{service.label}</strong>'

                if service.linked_product:
                    # Link to the linked product admin change page
                    try:
                        product_admin_url = reverse('admin:catalog_product_change', args=[service.linked_product.id])
                        product_link = f'<a href="{product_admin_url}" style="font-weight: bold; color: #447e9b;">{service.linked_product.name}</a>'
                    except Exception:
                        product_link = service.linked_product.name

                    html.append(f"<li style='margin-bottom: 5px;'>{service_link} &mdash; Связанный товар: {product_link}</li>")
                else:
                    html.append(f"<li style='margin-bottom: 5px;'>{service_link} &mdash; <span style='color: #888;'>Нет связанного товара</span></li>")
            else:
                html.append(f"<li style='margin-bottom: 5px; color: #cc1111;'>Услуга с ID {sid} не найдена в базе данных</li>")

        html.append("</ul>")
        return mark_safe("".join(html))

    additional_services_display.short_description = "Дополнительные услуги"


@admin.register(AdditionalService)
class AdditionalServiceAdmin(SortableAdminMixin, MakeFirstAdminMixin, admin.ModelAdmin):
    list_display = ["order", "label", "linked_product", "is_active"]
    list_editable = ["is_active"]
    search_fields = ["label"]
    autocomplete_fields = ["linked_product"]
    ordering = ["order"]



@admin.register(EventFormat)
class EventFormatAdmin(SortableAdminMixin, MakeFirstAdminMixin, admin.ModelAdmin):
    list_display = ["order", "name", "is_active"]
    list_editable = ["is_active"]
    search_fields = ["name"]
    ordering = ["order"]



