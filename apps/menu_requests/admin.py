from django.contrib import admin
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django.contrib import messages
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin, SortableAdminBase
from django.forms import Textarea, TextInput
from django.db import models
from .models import (
    MenuRequest,
    AdditionalService,
    EventFormat,
    CalculatePageSettings,
    CalculateFeature,
    CalculateBudgetOption,
    CalculateFoodOption,
    CalculateStep,
    CalculateFAQ,
)
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
        "budget",
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
                "fields": ["format", "guests", "budget", "date", "food_preferences"],
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
                from ..orders.email import send_menu_request_email_notification_sync
                send_menu_request_email_notification_sync(obj.id, raise_exception=True)
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


@admin.register(EventFormat)
class EventFormatAdmin(SortableAdminMixin, MakeFirstAdminMixin, admin.ModelAdmin):
    list_display = ["order", "name", "is_active"]
    list_editable = ["is_active"]
    search_fields = ["name"]
    ordering = ["order"]





class CalculateFeatureInline(SortableInlineAdminMixin, admin.TabularInline):
    model = CalculateFeature
    extra = 0
    fields = ["order", "icon", "title", "subtitle", "is_active"]
    ordering = ["order"]
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"style": "width: 100%;"})},
    }
    verbose_name = "Преимущество"
    verbose_name_plural = "1. Карточки преимуществ (под шапкой)"


class CalculateBudgetOptionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = CalculateBudgetOption
    extra = 0
    fields = ["order", "name", "is_active"]
    ordering = ["order"]
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"style": "width: 100%; min-width: 250px;"})},
    }
    verbose_name = "Опция бюджета"
    verbose_name_plural = "2. Опции примерного бюджета (в форме)"


class CalculateFoodOptionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = CalculateFoodOption
    extra = 0
    fields = ["order", "name", "is_active"]
    ordering = ["order"]
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"style": "width: 100%; min-width: 200px;"})},
    }
    verbose_name = "Вид блюда"
    verbose_name_plural = "3. Виды блюд (в форме)"


class AdditionalServiceInline(SortableInlineAdminMixin, admin.TabularInline):
    model = AdditionalService
    extra = 0
    fields = ["order", "label", "description", "linked_product", "is_active"]
    ordering = ["order"]
    autocomplete_fields = ["linked_product"]
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 2, "style": "width: 100%; min-width: 220px;"})},
    }
    verbose_name = "Дополнительная услуга"
    verbose_name_plural = "4. Дополнительные услуги (в форме)"


class CalculateStepInline(SortableInlineAdminMixin, admin.TabularInline):
    model = CalculateStep
    extra = 0
    fields = ["order", "step", "title", "text", "is_active"]
    ordering = ["order"]
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 2, "style": "width: 100%; min-width: 260px;"})},
    }
    verbose_name = "Шаг процесса"
    verbose_name_plural = "5. Шаги процесса («Как мы работаем»)"


class CalculateFAQInline(SortableInlineAdminMixin, admin.TabularInline):
    model = CalculateFAQ
    extra = 0
    fields = ["order", "question", "answer", "is_active"]
    ordering = ["order"]
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 3, "style": "width: 100%; min-width: 320px;"})},
    }
    verbose_name = "Вопрос FAQ"
    verbose_name_plural = "6. Вопросы и ответы (FAQ)"


@admin.register(CalculatePageSettings)
class CalculatePageSettingsAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = [
        CalculateFeatureInline,
        CalculateBudgetOptionInline,
        CalculateFoodOptionInline,
        AdditionalServiceInline,
        CalculateStepInline,
        CalculateFAQInline,
    ]
    readonly_fields = ["updated_at"]
    fieldsets = [
        (
            "Хиро-секция (Шапка страницы расчёта)",
            {
                "fields": ["hero_badge", "hero_title", "hero_description"],
            },
        ),
        (
            "Секция «Как мы работаем» (Заголовки)",
            {
                "fields": ["steps_title", "steps_subtitle"],
            },
        ),
        (
            "Секция FAQ (Заголовки)",
            {
                "fields": ["faq_title", "faq_subtitle"],
            },
        ),
        (
            "SEO (Поисковая оптимизация страницы)",
            {
                "fields": ["seo_title", "seo_description"],
            },
        ),
        (
            "Служебная информация",
            {
                "fields": ["updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]

    class Media:
        css = {
            "all": ["admin/css/sortable_custom.css?v=2026_drag_v2"]
        }
        js = [
            "admin/js/sortable_inline_arrows.js?v=2026_drag_v3",
        ]

    def changelist_view(self, request, extra_context=None):
        obj = CalculatePageSettings.load()
        return HttpResponseRedirect(
            reverse("admin:menu_requests_calculatepagesettings_change", args=[obj.pk])
        )

    def has_add_permission(self, request):
        return not CalculatePageSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
