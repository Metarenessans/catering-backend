from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.mail import get_connection, send_mail
from .models import SystemSettings
from apps.catalog.revalidate import notify_frontend_revalidate


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ["__str__", "frontend_url", "email_host_user", "updated_at"]
    readonly_fields = ["cache_actions_display", "email_test_display", "updated_at"]

    fieldsets = [
        (
            "Связь с сайтом (Next.js) и сброс кэша",
            {
                "fields": [
                    "frontend_url",
                    "revalidation_secret",
                    "site_url",
                    "cache_actions_display",
                ],
                "description": (
                    "Настройки для отправки сигналов сброса кэша микроразметки и страниц при изменениях в админке.<br>"
                    "<b>URL фронтенда:</b> <code>http://127.0.0.1:3000</code> локально или <code>https://chefmil-furshet.ru</code> на боевом сервере.<br>"
                    "<b>Основной адрес сайта:</b> используется в ссылках в письмах клиентам и Telegram-уведомлениях."
                ),
            },
        ),
        (
            "Отправка Email (SMTP)",
            {
                "fields": [
                    "email_host",
                    "email_port",
                    "email_use_ssl",
                    "email_use_tls",
                    "email_host_user",
                    "email_host_password",
                    "default_from_email",
                    "email_test_display",
                ],
                "description": (
                    "Настройки почтового ящика для отправки уведомлений о заказах и подборах меню.<br>"
                    "Если поля не заполнены, система автоматически использует параметры из <code>.env</code>.<br>"
                    "Для Яндекс Почты используйте <b>хост:</b> <code>smtp.yandex.ru</code>, <b>порт:</b> <code>465</code>, <b>SSL:</b> включен, "
                    "и специальный <b>пароль приложения</b> из личного кабинета Яндекс ID."
                ),
            },
        ),
        (
            "Интеграция с Telegram",
            {
                "fields": ["telegram_bot_token", "telegram_bot_proxy"],
                "description": (
                    "Настройки Telegram-бота для отправки уведомлений администраторам.<br>"
                    "<b>Токен бота:</b> создается в <code>@BotFather</code> (если не указан, берется из <code>.env</code>).<br>"
                    "<b>Прокси:</b> поддерживаются форматы <code>socks5://user:pass@host:port</code>, <code>http://user:pass@host:port</code> или <code>host:port:user:pass</code>."
                ),
            },
        ),
        (
            "SEO и карта сайта (Sitemap)",
            {
                "fields": ["sitemap_cache_minutes"],
                "description": (
                    "Управление временем жизни кэша для <code>/sitemap.xml</code>.<br>"
                    "<b>0</b> — генерация на лету (force-dynamic): каждое обращение запрашивает свежие данные.<br>"
                    "<b>> 0</b> (например, 30 или 60) — кэширование на указанное количество минут для максимальной скорости."
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

    def cache_actions_display(self, obj):
        url = reverse("admin:system_settings_revalidate_cache")
        return mark_safe(
            f'''
            <div style="margin-top: 5px;">
                <a href="{url}" class="button" style="background-color: #264b5d; color: white; padding: 6px 14px; text-decoration: none; border-radius: 4px; font-weight: 500;">
                    🔄 Сбросить весь кэш сайта (Next.js) сейчас
                </a>
                <span style="margin-left: 10px; color: #666; font-size: 13px;">Отправляет сигнал на {obj.get_frontend_url()}</span>
            </div>
            '''
        )
    cache_actions_display.short_description = "Действие"

    def email_test_display(self, obj):
        url = reverse("admin:system_settings_send_test_email")
        return mark_safe(
            f'''
            <div style="margin-top: 5px;">
                <a href="{url}" class="button" style="background-color: #28a745; color: white; padding: 6px 14px; text-decoration: none; border-radius: 4px; font-weight: 500;">
                    ✉️ Отправить тестовое письмо
                </a>
                <span style="margin-left: 10px; color: #666; font-size: 13px;">Проверяет подключение к SMTP-серверу и отправку</span>
            </div>
            '''
        )
    email_test_display.short_description = "Тестирование почты"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "revalidate-cache/",
                self.admin_site.admin_view(self.revalidate_cache_view),
                name="system_settings_revalidate_cache",
            ),
            path(
                "send-test-email/",
                self.admin_site.admin_view(self.send_test_email_view),
                name="system_settings_send_test_email",
            ),
        ]
        return custom_urls + urls

    def revalidate_cache_view(self, request):
        obj = SystemSettings.load()
        try:
            notify_frontend_revalidate(event_type="all")
            messages.success(
                request,
                f"Сигнал на сброс кэша успешно отправлен на фронтенд ({obj.get_frontend_url()})!"
            )
        except Exception as e:
            messages.error(request, f"Ошибка при отправке вебхука: {e}")

        return HttpResponseRedirect(
            reverse("admin:system_settings_systemsettings_change", args=[obj.pk])
        )

    def send_test_email_view(self, request):
        obj = SystemSettings.load()
        cfg = obj.get_email_config()

        if not cfg["host"] or not cfg["user"]:
            messages.error(
                request,
                "SMTP Сервер или Email / Логин не настроены ни в админке, ни в .env!"
            )
            return HttpResponseRedirect(
                reverse("admin:system_settings_systemsettings_change", args=[obj.pk])
            )

        recipient = request.user.email or cfg["user"]
        try:
            conn = get_connection(
                host=cfg["host"],
                port=cfg["port"],
                username=cfg["user"],
                password=cfg["password"],
                use_ssl=cfg["use_ssl"],
                use_tls=cfg["use_tls"],
                fail_silently=False,
            )
            message_body = (
                "Это тестовое письмо для проверки SMTP-настроек сайта.\n\n"
                "Отправлено из админки Django.\n"
                f"Хост: {cfg['host']}:{cfg['port']}\n"
                f"Отправитель: {cfg['from_email']}\n"
                f"Получатель: {recipient}\n"
            )
            send_mail(
                subject="Тестовое сообщение | Шеф Мил Фуршет",
                message=message_body,
                from_email=cfg["from_email"],
                recipient_list=[recipient],
                connection=conn,
                fail_silently=False,
            )
            messages.success(
                request,
                f"Тестовое письмо успешно отправлено на {recipient} через {cfg['host']}:{cfg['port']}!"
            )
        except Exception as e:
            messages.error(
                request,
                f"Ошибка отправки через {cfg['host']}:{cfg['port']}: {e}"
            )

        return HttpResponseRedirect(
            reverse("admin:system_settings_systemsettings_change", args=[obj.pk])
        )

    def changelist_view(self, request, extra_context=None):
        """Перенаправляет сразу на редактирование синглтона."""
        obj = SystemSettings.load()
        return HttpResponseRedirect(
            reverse("admin:system_settings_systemsettings_change", args=[obj.pk])
        )

    def has_add_permission(self, request):
        return not SystemSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
