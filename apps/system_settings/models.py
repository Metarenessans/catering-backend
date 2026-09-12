import os
from django.db import models
from django.conf import settings


class SystemSettings(models.Model):
    """
    Глобальные системные настройки сервиса (Singleton).
    """
    # 1. SEO и карта сайта (Sitemap)
    sitemap_cache_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Кэширование sitemap (мин)",
        help_text="0 — генерация на лету (force-dynamic). Значение > 0 (например, 30 или 60) — кэширование на указанное количество минут.",
    )
    enable_debug_json_file = models.BooleanField(
        default=False,
        verbose_name="Генерация JSON файла микроразметки для деф-режима",
        help_text="При включении создает и обновляет файл schema_markup_debug.json в корне проекта при переходе по страницам. По умолчанию выключено для исключения лишней нагрузки на диск.",
    )

    # 2. Связь с фронтендом (Next.js Revalidation Webhook)
    frontend_url = models.CharField(
        max_length=255,
        default="http://127.0.0.1:3000",
        blank=True,
        verbose_name="URL фронтенда (Next.js)",
        help_text="Адрес фронтенда для отправки вебхуков сброса кэша (локально: http://127.0.0.1:3000, на проде: https://chefmil-furshet.ru).",
    )
    revalidation_secret = models.CharField(
        max_length=255,
        default="catering_schema_secret_key_2026",
        blank=True,
        verbose_name="Секретный ключ вебхука",
        help_text="Секретный токен для авторизации запросов сброса кэша Next.js (REVALIDATION_SECRET).",
    )
    site_url = models.CharField(
        max_length=255,
        default="https://chefmil-furshet.ru",
        blank=True,
        verbose_name="Основной адрес сайта",
        help_text="Используется для формирования ссылок на сайт и карточки в админке в уведомлениях.",
    )

    # 3. Отправка Email (SMTP)
    email_host = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="SMTP Сервер (Хост)",
        help_text="Например: smtp.yandex.ru. Если не заполнено, берется из .env.",
    )
    email_port = models.PositiveIntegerField(
        default=465,
        verbose_name="Порт SMTP",
        help_text="Обычно 465 для SSL или 587 для TLS.",
    )
    email_use_ssl = models.BooleanField(
        default=True,
        verbose_name="Использовать SSL",
    )
    email_use_tls = models.BooleanField(
        default=False,
        verbose_name="Использовать TLS",
    )
    email_host_user = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Email / Логин SMTP",
        help_text="Почтовый ящик для отправки (например: chef-meal@yandex.com). Если не заполнено, берется из .env.",
    )
    email_host_password = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Пароль приложения SMTP",
        help_text="Пароль приложения для почты (например, созданный в Яндекс ID). Если не заполнено, берется из .env.",
    )
    default_from_email = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Email отправителя (From)",
        help_text="Отображаемый адрес отправителя. Если пусто, совпадает с Email / Логином SMTP.",
    )

    # 4. Интеграция с Telegram
    telegram_bot_token = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Токен Telegram-бота",
        help_text="Токен бота от @BotFather (например: 123456789:ABCdefGHI...). Если не заполнено, берется из .env.",
    )
    telegram_bot_proxy = models.CharField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="Прокси для Telegram-бота",
        help_text="URL или строка прокси (например: socks5://user:pass@host:port, http://user:pass@host:port или host:port:user:pass).",
    )

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Настройки системы"
        verbose_name_plural = "Настройки системы"

    def __str__(self):
        return "Настройки системы"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def get_frontend_url(self) -> str:
        url = self.frontend_url or getattr(settings, "FRONTEND_URL", "http://127.0.0.1:3000")
        return url.rstrip("/")

    def get_revalidation_secret(self) -> str:
        return self.revalidation_secret or getattr(settings, "REVALIDATION_SECRET", "catering_schema_secret_key_2026")

    def get_site_url(self) -> str:
        url = self.site_url or os.getenv("ADMIN_BASE_URL", "https://chefmil-furshet.ru")
        return url.rstrip("/")

    def get_telegram_bot_token(self) -> str:
        return self.telegram_bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")

    def get_email_config(self) -> dict:
        host = self.email_host or getattr(settings, "EMAIL_HOST", "") or os.getenv("EMAIL_HOST", "")
        port = self.email_port or getattr(settings, "EMAIL_PORT", 465)
        user = self.email_host_user or getattr(settings, "EMAIL_HOST_USER", "") or os.getenv("EMAIL_HOST_USER", "")
        password = self.email_host_password or getattr(settings, "EMAIL_HOST_PASSWORD", "") or os.getenv("EMAIL_HOST_PASSWORD", "")
        use_ssl = self.email_use_ssl if self.email_host else getattr(settings, "EMAIL_USE_SSL", True)
        use_tls = self.email_use_tls if self.email_host else getattr(settings, "EMAIL_USE_TLS", False)
        from_email = self.default_from_email or os.getenv("DEFAULT_FROM_EMAIL", getattr(settings, "DEFAULT_FROM_EMAIL", user))
        return {
            "host": host,
            "port": int(port),
            "user": user,
            "password": password,
            "use_ssl": use_ssl,
            "use_tls": use_tls,
            "from_email": from_email,
        }
