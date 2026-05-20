from django.contrib import admin
from django.utils.safestring import mark_safe
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from .models import Category, Product, ProductExtraInfo, ProductOption


class ProductExtraInfoInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProductExtraInfo
    extra = 1
    fields = ["amount", "unit"]
    ordering = ["order"]


class ProductOptionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProductOption
    extra = 1
    fields = ["name", "price", "old_price"]
    ordering = ["order"]


@admin.register(Category)
class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["name", "slug", "order", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "slug"]
    ordering = ["order"]
    list_editable = ["is_active"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "price",
        "image_preview",
        "is_active",
        "is_featured",
        "order",
        "created_at",
    ]
    list_filter = ["category", "is_active", "is_featured"]
    search_fields = ["name", "description"]
    ordering = ["order"]
    list_editable = ["price", "is_active", "is_featured"]
    autocomplete_fields = ["category"]
    inlines = [ProductExtraInfoInline, ProductOptionInline]
    readonly_fields = ["image_preview", "created_at", "updated_at"]


    def image_preview(self, obj):
        url = obj.effective_image_url
        if url:
            return mark_safe(f'<img src="{url}" width="100" style="border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />')
        return "Нет фото"

    image_preview.short_description = "Предпросмотр"
    fieldsets = [
        (
            "Основная информация",
            {
                "fields": ["name", "category", "description", "order"],
            },
        ),
        (
            "Цены",
            {
                "fields": ["price", "old_price"],
            },
        ),
        (
            "Изображение",
            {
                "fields": ["image", "image_url", "image_preview"],
                "description": "Загрузите изображение или укажите внешний URL.",
            },
        ),
        (
            "Статус",
            {
                "fields": ["is_active", "is_featured"],
            },
        ),
        (
            "Служебная информация",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]
