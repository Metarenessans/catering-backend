from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from adminsortable2.admin import SortableAdminMixin
from .models import CompanyInfo, LegalDocument, PrivacyPolicy
from ..catalog.mixins import MakeFirstAdminMixin


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ["company_name", "phone_number", "email", "updated_at"]
    readonly_fields = [
        "updated_at",
        "hero_image_top_preview",
        "hero_image_top_mobile_preview",
        "hero_image_bottom_preview",
        "og_image_preview",
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
                    "rkn_registry_url",
                    "rkn_registry_number",
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
            "Изображение для соцсетей и мессенджеров (Open Graph)",
            {
                "fields": [
                    "og_image",
                    "og_image_preview",
                ],
                "description": (
                    "<b>Основное изображение Open Graph (og:image)</b> для формирования красивого превью ссылки "
                    "в Telegram, ВКонтакте, WhatsApp и сниппетах поисковиков.<br>"
                    "Рекомендуется горизонтальное изображение с соотношением сторон <b>1.91:1 (1200×630 px)</b>.<br>"
                    "<i>Отображается на всех страницах сайта, кроме карточек товаров и отдельных статей блога.</i>"
                ),
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

    def og_image_preview(self, obj):
        if obj.og_image:
            return mark_safe(f'<img src="{obj.og_image.url}" width="240" style="border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.15); border: 1px solid rgba(255,255,255,0.1);" />')
        return "Нет изображения"
    og_image_preview.short_description = "Предпросмотр OG Image"

    def has_add_permission(self, request):
        """Разрешаем создание только если записи нет."""
        return not CompanyInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Запрещаем удаление singleton-записи."""
        return False


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "has_file", "updated_at", "view_on_site_link"]
    list_display_links = ["title"]
    readonly_fields = ["updated_at", "html_preview", "live_page_link"]
    search_fields = ["title", "slug"]

    fieldsets = [
        (
            "Основная информация",
            {
                "fields": ["title", "slug", "live_page_link"],
            },
        ),
        (
            "Загрузка документа (автоматическая конвертация в HTML)",
            {
                "fields": ["file"],
                "description": (
                    "<b>Загрузите файл документа</b> (.docx, .pdf, .md, .html, .txt).<br>"
                    "При сохранении файл будет автоматически сконвертирован в семантический HTML-код "
                    "и подставлен в поле ниже.<br>"
                    "<i>Рекомендуется формат Microsoft Word (.docx) для наилучшей разметки заголовков и списков.</i>"
                ),
            },
        ),
        (
            "HTML-содержимое",
            {
                "fields": ["content_html"],
                "description": (
                    "Сгенерированный HTML-код документа. Вы также можете отредактировать его напрямую "
                    "или вставить собственный код."
                ),
            },
        ),
        (
            "Визуальный предпросмотр",
            {
                "fields": ["html_preview"],
            },
        ),
        (
            "Служебная информация",
            {
                "fields": ["order", "updated_at"],
            },
        ),
    ]

    def has_file(self, obj):
        return bool(obj.file)
    has_file.boolean = True
    has_file.short_description = "Файл загружен"

    def html_preview(self, obj):
        if not obj.content_html:
            return mark_safe("<em>HTML-содержимое пока пустое. Загрузите файл выше или введите HTML.</em>")
        return mark_safe(
            '<div style="max-height: 450px; overflow-y: auto; padding: 20px; '
            'background: #181818; color: #f0f0f0; border: 1px solid #333; '
            'border-radius: 8px; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; '
            'line-height: 1.7; font-size: 14px;">'
            f'{obj.content_html}'
            '</div>'
        )
    html_preview.short_description = "Визуальный предпросмотр"

    def live_page_link(self, obj):
        if not obj.slug:
            return "-"
        from apps.system_settings.models import SystemSettings
        frontend_url = SystemSettings.load().get_frontend_url()
        return mark_safe(
            f'<a href="{frontend_url}/{obj.slug}" target="_blank" '
            f'style="display: inline-block; padding: 6px 14px; background: #db4900; '
            f'color: #fff; text-decoration: none; border-radius: 4px; font-weight: 500;">'
            f'Открыть на сайте (/{obj.slug}) ↗'
            f'</a>'
        )
    live_page_link.short_description = "Просмотр на сайте"

    def view_on_site_link(self, obj):
        if not obj.slug:
            return "-"
        from apps.system_settings.models import SystemSettings
        frontend_url = SystemSettings.load().get_frontend_url()
        return mark_safe(
            f'<a href="{frontend_url}/{obj.slug}" target="_blank" style="color: #db4900; font-weight: 500;">'
            f'На сайте ↗</a>'
        )
    view_on_site_link.short_description = "Ссылка"

    def save_model(self, request, obj, form, change):
        if "file" in form.changed_data and form.cleaned_data.get("file"):
            uploaded_file = form.cleaned_data["file"]
            try:
                from .doc_converter import convert_document_to_html
                converted_html = convert_document_to_html(uploaded_file)
                if converted_html:
                    obj.content_html = converted_html
                    messages.success(
                        request,
                        f"Файл «{uploaded_file.name}» успешно сконвертирован в HTML!"
                    )
                else:
                    messages.warning(
                        request,
                        f"Файл «{uploaded_file.name}» обработан, но содержимое пустое."
                    )
            except Exception as e:
                messages.error(
                    request,
                    f"Ошибка при конвертации файла «{uploaded_file.name}»: {e}"
                )
        super().save_model(request, obj, form, change)







