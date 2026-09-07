from django.contrib import admin
from django.utils.safestring import mark_safe
from adminsortable2.admin import SortableAdminMixin
from .models import CompanyInfo, FooterNavigation
from ..catalog.mixins import MakeFirstAdminMixin


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ["company_name", "phone_number", "email", "updated_at"]
    readonly_fields = [
        "updated_at",
        "hero_image_top_preview",
        "hero_image_top_mobile_preview",
        "hero_image_bottom_preview",
    ]

    fieldsets = [
        (
            "Основная информация и реквизиты",
            {
                "fields": [
                    "company_name",
                    "legal_name",
                    "city",
                    "address",
                    "inn",
                    "ogrn",
                ],
            },
        ),
        (
            "Микроразметка Schema.org / Геолокация (SEO)",
            {
                "fields": [
                    "latitude",
                    "longitude",
                    "price_range",
                    "serves_cuisine",
                ],
                "description": "Поля для поисковой микроразметки (Яндекс / Google). Если оставить пустыми, они не будут выводиться в Schema.org.",
            },
        ),
        (
            "Контакты и ссылки",
            {
                "fields": [
                    "phone_number",
                    "email",
                    "telegram",
                    "max_messenger",
                    "vk",
                    "reviews_url",
                ],
            },
        ),
        (
            "Финансы и доставка",
            {
                "fields": ["min_order_amount", "free_delivery_threshold", "delivery_cost"],
            },
        ),
        (
            "Изображения хиро-секции",
            {
                "fields": [
                    "hero_image_top",
                    "hero_image_top_preview",
                    "hero_image_top_mobile",
                    "hero_image_top_mobile_preview",
                    "hero_image_bottom",
                    "hero_image_bottom_preview",
                ],
            },
        ),
        (
            "Служебная информация",
            {
                "fields": ["updated_at"],
            },
        ),
    ]

    def hero_image_top_preview(self, obj):
        if obj.hero_image_top:
            return mark_safe(f'<img src="{obj.hero_image_top.url}" width="150" style="border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />')
        return "Нет фото"
    hero_image_top_preview.short_description = "Предпросмотр верхнего изображения"

    def hero_image_top_mobile_preview(self, obj):
        if obj.hero_image_top_mobile:
            return mark_safe(f'<img src="{obj.hero_image_top_mobile.url}" width="150" style="border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />')
        return "Нет фото"
    hero_image_top_mobile_preview.short_description = "Предпросмотр мобильного верхнего изображения"

    def hero_image_bottom_preview(self, obj):
        if obj.hero_image_bottom:
            return mark_safe(f'<img src="{obj.hero_image_bottom.url}" width="150" style="border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />')
        return "Нет фото"
    hero_image_bottom_preview.short_description = "Предпросмотр нижнего изображения"

    def has_add_permission(self, request):
        """Разрешаем создание только если записи нет."""
        return not CompanyInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Запрещаем удаление singleton-записи."""
        return False


@admin.register(FooterNavigation)
class FooterNavigationAdmin(SortableAdminMixin, MakeFirstAdminMixin, admin.ModelAdmin):
    list_display = ["order", "category"]
    list_filter = ["category"]
    ordering = ["order"]


