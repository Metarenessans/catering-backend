from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from adminsortable2.admin import SortableAdminMixin
from .models import MenuRequest, AdditionalService, EventFormat


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
            "Служебная информация",
            {
                "fields": ["created_at", "updated_at", "additional_services"],
                "classes": ["collapse"],
            },
        ),
    ]

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
class AdditionalServiceAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["order", "label", "linked_product", "is_active"]
    list_editable = ["is_active"]
    search_fields = ["label"]
    autocomplete_fields = ["linked_product"]
    ordering = ["order"]

    class Media:
        css = {
            "all": ("admin/css/sortable_custom.css",)
        }


@admin.register(EventFormat)
class EventFormatAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["order", "name", "is_active"]
    list_editable = ["is_active"]
    search_fields = ["name"]
    ordering = ["order"]

    class Media:
        css = {
            "all": ("admin/css/sortable_custom.css",)
        }

