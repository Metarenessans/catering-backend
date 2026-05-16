from django.db import models
from apps.catalog.models import Category


class CompanyInfo(models.Model):
    """
    Информация о компании — единственная запись (singleton).
    Соответствует интерфейсу CompanyInfo из frontend/src/mock-data.ts.
    """
    company_name = models.CharField(max_length=200, verbose_name="Название компании")
    address = models.CharField(max_length=500, verbose_name="Адрес")
    inn = models.CharField(max_length=20, blank=True, default="", verbose_name="ИНН")
    ogrn = models.CharField(max_length=20, blank=True, default="", verbose_name="ОГРН")
    phone_number = models.CharField(max_length=30, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    telegram = models.URLField(max_length=300, blank=True, default="", verbose_name="Telegram")
    max_messenger = models.URLField(
        max_length=300, blank=True, default="", verbose_name="MAX мессенджер"
    )
    reviews_url = models.URLField(
        max_length=1000,
        blank=True,
        default="",
        verbose_name="Ссылка на отзывы (Авито)",
    )
    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=5000,
        verbose_name="Минимальная сумма заказа (₽)",
    )
    free_delivery_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=10000,
        verbose_name="Порог бесплатной доставки (₽)",
    )
    delivery_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1500,
        verbose_name="Стоимость доставки (₽)",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Информация о компании"
        verbose_name_plural = "Информация о компании"

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        """Обеспечивает только одну запись (singleton pattern)."""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "company_name": "Шеф Мил",
                "address": "423800, Набережные Челны, ул. Абрикосовая, 10",
                "inn": "1234567890",
                "ogrn": "1234567890123",
                "phone_number": "79274661333",
                "email": "chef-meal@mail.ru",
                "telegram": "https://t.me/Lyud_MILKA9",
                "max_messenger": "https://max.me/Lyud_MILKA9",
                "reviews_url": "https://www.avito.ru/user/6df047abcc3b2820419afccd9491017e/profile/all/predlozheniya_uslug?src=sharing&sellerId=6df047abcc3b2820419afccd9491017e",
            },
        )
        return obj


class FooterNavigation(models.Model):
    """
    Элементы навигации в футере (раздел КАТАЛОГ).
    Связаны с реальными категориями каталога.
    """
    name = models.CharField(max_length=100, verbose_name="Текст ссылки")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="footer_navs",
        verbose_name="Категория",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")

    class Meta:
        verbose_name = "Навигация в футере"
        verbose_name_plural = "Навигация в футере"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name
