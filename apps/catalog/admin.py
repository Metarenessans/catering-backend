from django.contrib import admin
from .models import Category, Product, ProductExtraInfo


class ProductExtraInfoInline(admin.TabularInline):
    model = ProductExtraInfo
    extra = 1
    fields = ["amount", "unit", "order"]
    ordering = ["order"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "slug"]
    ordering = ["order", "name"]
    list_editable = ["order", "is_active"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "price",
        "old_price",
        "is_active",
        "is_featured",
        "order",
        "created_at",
    ]
    list_filter = ["category", "is_active", "is_featured"]
    search_fields = ["name", "description"]
    ordering = ["order", "name"]
    list_editable = ["price", "is_active", "is_featured", "order"]
    autocomplete_fields = ["category"]
    inlines = [ProductExtraInfoInline]
    readonly_fields = ["created_at", "updated_at"]
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
                "fields": ["image", "image_url"],
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
