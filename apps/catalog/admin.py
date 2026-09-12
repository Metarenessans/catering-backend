from django.contrib import admin
from django.utils.safestring import mark_safe
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from .models import Section, Category, SectionCategory, Product, ProductExtraInfo, ProductOption
from .mixins import MakeFirstAdminMixin


class CategoryProductInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Product
    extra = 0
    fields = [
        "order",
        "image_preview",
        "name",
        "price",
        "is_active",
        "is_featured",
    ]
    readonly_fields = ["image_preview"]
    ordering = ["order"]
    verbose_name = "Товар в категории"
    verbose_name_plural = "Товары в этой категории (перетаскивайте или используйте стрелки для смены порядка)"
    show_change_link = True

    def image_preview(self, obj):
        if obj and obj.pk:
            url = obj.effective_image_url
            if url:
                return mark_safe(
                    f'<img src="{url}" width="42" height="42" style="object-fit: cover; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);" />'
                )
        return "—"

    image_preview.short_description = "Фото"


class SectionCategoryInline(SortableInlineAdminMixin, admin.TabularInline):
    model = SectionCategory
    extra = 1
    fields = ["category", "order"]
    ordering = ["order"]
    verbose_name = "Категория в разделе"
    verbose_name_plural = "Категории в этом разделе (перетаскивайте или используйте стрелки для смены порядка)"


class ProductExtraInfoInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProductExtraInfo
    extra = 1
    fields = ["amount", "unit", "is_active", "order"]
    ordering = ["order"]



class ProductOptionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProductOption
    extra = 1
    fields = ["name", "price", "old_price", "min_order_quantity", "is_active", "order"]
    ordering = ["order"]



@admin.register(Section)
class SectionAdmin(SortableAdminMixin, MakeFirstAdminMixin, admin.ModelAdmin):
    list_display = ["order", "name", "slug", "get_categories_count", "image_preview", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "slug"]
    ordering = ["order"]
    list_editable = ["is_active"]
    readonly_fields = ["image_preview", "created_at"]
    inlines = [SectionCategoryInline]

    class Media:
        css = {
            "all": ["admin/css/sortable_custom.css?v=2026_drag_v2"]
        }
        js = [
            "admin/js/sortable_inline_arrows.js?v=2026_drag_v3",
            "admin/js/slug_auto_update.js?v=2026_icon",
        ]

    fieldsets = [
        (
            "Основная информация",
            {
                "fields": ["name", "slug", "order", "is_active"],
            },
        ),
        (
            "Изображение раздела",
            {
                "fields": ["image", "image_url", "image_preview"],
                "description": "Загрузите изображение или укажите внешний URL.",
            },
        ),
        (
            "Служебная информация",
            {
                "fields": ["created_at"],
                "classes": ["collapse"],
            },
        ),
    ]

    def image_preview(self, obj):
        url = obj.effective_image_url
        if url:
            return mark_safe(f'<img src="{url}" width="100" style="border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />')
        return "Нет фото"

    image_preview.short_description = "Предпросмотр"

    def get_categories_count(self, obj):
        return obj.categories.count()

    get_categories_count.short_description = "Категорий в разделе"


@admin.register(Category)
class CategoryAdmin(SortableAdminMixin, MakeFirstAdminMixin, admin.ModelAdmin):
    list_display = ["order", "name", "get_sections", "get_products_count", "slug", "is_active"]
    list_filter = ["sections", "is_active"]
    search_fields = ["name", "slug"]
    ordering = ["order"]
    list_editable = ["is_active"]
    inlines = [CategoryProductInline]

    class Media:
        css = {
            "all": ["admin/css/sortable_custom.css?v=2026_drag_v2"]
        }
        js = [
            "admin/js/sortable_inline_arrows.js?v=2026_drag_v3",
            "admin/js/slug_auto_update.js?v=2026_icon",
        ]

    def get_sections(self, obj):
        sections = list(obj.sections.values_list("name", flat=True))
        return ", ".join(sections) if sections else "—"

    get_sections.short_description = "Разделы"

    def get_products_count(self, obj):
        return obj.products.count()

    get_products_count.short_description = "Товаров"



@admin.register(Product)
class ProductAdmin(SortableAdminMixin, MakeFirstAdminMixin, admin.ModelAdmin):
    sortable_group_by = "category"
    list_display = [
        "order",
        "name",
        "slug",
        "category",
        "price",
        "image_preview",
        "is_active",
        "is_featured",
        "created_at",
    ]
    list_filter = ["category", "is_active", "is_featured"]
    search_fields = ["name", "slug", "description"]
    ordering = ["order"]
    list_editable = ["price", "is_active", "is_featured"]
    autocomplete_fields = ["category"]

    def get_extra_model_filters(self, request):
        filters = {}
        category_id = request.GET.get("category__id__exact")
        if category_id:
            filters["category_id"] = category_id
        return filters
    inlines = [ProductExtraInfoInline, ProductOptionInline]
    readonly_fields = ["image_preview", "created_at", "updated_at"]

    class Media:
        css = {
            "all": ["admin/css/sortable_custom.css?v=2026_drag_v2"]
        }
        js = [
            "admin/js/sortable_inline_arrows.js?v=2026_drag_v3",
            "admin/js/slug_auto_update.js?v=2026_icon",
        ]

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
                "fields": ["name", "slug", "category", "description", "order"],
            },
        ),
        (
            "Цены и ограничения",
            {
                "fields": ["price", "old_price", "min_order_quantity"],
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
