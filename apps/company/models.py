from django.db import models
from ..catalog.models import Category


class CompanyInfo(models.Model):
    """
    Информация о компании — единственная запись (singleton).
    Соответствует интерфейсу CompanyInfo из frontend/src/mock-data.ts.
    """
    company_name = models.CharField(max_length=200, verbose_name="Название компании")
    legal_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Юридическое название",
        help_text="Официальное юр. лицо (например: ИП или ООО). Если пусто, в разметке используется название компании.",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Город",
        help_text="Город для Schema.org PostalAddress (addressLocality)",
    )
    address = models.CharField(max_length=500, verbose_name="Адрес")
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Широта (latitude)",
        help_text="Географическая широта для карт и Schema.org (например: 55.743821). Если не заполнено, geo-блок не выводится.",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Долгота (longitude)",
        help_text="Географическая долгота для карт и Schema.org (например: 52.408215). Если не заполнено, geo-блок не выводится.",
    )
    price_range = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Ценовой диапазон",
        help_text="Для Schema.org (например: ₽₽). Если пусто, не выводится.",
    )
    serves_cuisine = models.CharField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="Кухни / направления блюд",
        help_text="Через запятую для Schema.org servesCuisine. Если пусто, не выводится.",
    )
    inn = models.CharField(max_length=20, blank=True, default="", verbose_name="ИНН")
    ogrn = models.CharField(max_length=20, blank=True, default="", verbose_name="ОГРН")
    phone_number = models.CharField(max_length=30, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    telegram = models.URLField(max_length=300, blank=True, default="", verbose_name="Telegram")
    max_messenger = models.URLField(
        max_length=300, blank=True, default="", verbose_name="MAX мессенджер"
    )
    vk = models.URLField(
        max_length=300, blank=True, default="", verbose_name="ВКонтакте"
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
    hero_image_top = models.ImageField(
        upload_to="hero/",
        null=True,
        blank=True,
        verbose_name="Изображение для хиро-секции (верхнее)",
    )
    hero_image_top_mobile = models.ImageField(
        upload_to="hero/",
        null=True,
        blank=True,
        verbose_name="Изображение для хиро-секции (верхнее, мобильное)",
    )
    hero_image_bottom = models.ImageField(
        upload_to="hero/",
        null=True,
        blank=True,
        verbose_name="Изображение для хиро-секции (нижнее)",
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
                "legal_name": "",
                "city": "",
                "address": "",
                "latitude": None,
                "longitude": None,
                "price_range": "",
                "serves_cuisine": "",
                "inn": "",
                "ogrn": "",
                "phone_number": "",
                "email": "",
                "telegram": "",
                "max_messenger": "",
                "vk": "",
                "reviews_url": "",
            },
        )
        return obj


class FooterNavigation(models.Model):
    """
    Элементы навигации в футере (раздел КАТАЛОГ).
    Связаны с реальными категориями каталога.
    """
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
        ordering = ["order", "category__name"]

    def __str__(self):
        return self.category.name if self.category else f"FooterNav #{self.id}"
