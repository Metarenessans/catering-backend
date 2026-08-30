from django.db import models


class SystemSettings(models.Model):
    """
    Глобальные системные настройки сервиса (Singleton).
    """
    telegram_bot_proxy = models.CharField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="Прокси для Telegram-бота",
        help_text="URL или строка прокси (например: socks5://user:pass@host:port, http://user:pass@host:port или host:port:user:pass)",
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
