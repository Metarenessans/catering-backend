from django.contrib import admin
from .models import SystemSettings


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ["__str__", "telegram_bot_proxy", "updated_at"]
    readonly_fields = ["updated_at"]

    fieldsets = [
        (
            "Интеграция с Telegram",
            {
                "fields": ["telegram_bot_proxy"],
                "description": "Укажите прокси для Telegram-бота и отправки уведомлений. "
                               "Поддерживаются форматы: socks5://user:pass@host:port, "
                               "http://user:pass@host:port или host:port:user:pass.",
            },
        ),
        (
            "Служебная информация",
            {
                "fields": ["updated_at"],
            },
        ),
    ]

    def has_add_permission(self, request):
        """Разрешаем создание только если записи еще нет."""
        return not SystemSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Запрещаем удаление настроек."""
        return False
