from django.contrib import admin
from .models import MenuRequest, AdditionalService, EventFormat


@admin.register(MenuRequest)
class MenuRequestAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "phone",
        "format",
        "guests",
        "date",
        "status",
        "created_at",
    ]
    list_filter = ["status", "format", "date"]
    search_fields = ["name", "phone", "format"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at", "food_preferences", "additional_services"]
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
                "fields": ["name", "phone", "consent"],
            },
        ),
        (
            "Услуги",
            {
                "fields": ["additional_services"],
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
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]


@admin.register(AdditionalService)
class AdditionalServiceAdmin(admin.ModelAdmin):
    list_display = ["label", "order", "is_active"]
    list_editable = ["order", "is_active"]
    search_fields = ["label"]
    ordering = ["order"]


@admin.register(EventFormat)
class EventFormatAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "is_active"]
    list_editable = ["order", "is_active"]
    search_fields = ["name"]
    ordering = ["order"]
