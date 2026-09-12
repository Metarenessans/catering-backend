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
    rkn_registry_url = models.URLField(
        max_length=1000,
        blank=True,
        default="",
        verbose_name="Реестр операторов Роскомнадзора (ссылка)",
        help_text="Ссылка на запись в реестре РКН (например: https://pd.rkn.gov.ru/operators-registry/operators-list/?id=16-25-059794)",
    )
    rkn_registry_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Номер в реестре РКН",
        help_text="Определяется автоматически из ссылки (например: 16-25-059794), либо можно указать вручную.",
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
    og_image = models.ImageField(
        upload_to="company/",
        null=True,
        blank=True,
        verbose_name="Изображение для соцсетей (OG Image)",
        help_text="Основное изображение Open Graph для отображения ссылки на сайт в Telegram, VK, WhatsApp и поисковиках. Рекомендуется соотношение 1.91:1 (например, 1200x630 px). Используется на всех страницах сайта, кроме карточек товаров и отдельных статей блога.",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Информация о компании"
        verbose_name_plural = "Информация о компании"

    def __str__(self):
        return self.company_name

    def extract_rkn_number(self) -> str:
        """Автоматически извлекает номер оператора из ссылки реестра РКН."""
        if self.rkn_registry_number:
            return self.rkn_registry_number
        if not self.rkn_registry_url:
            return ""
        import urllib.parse
        import re
        try:
            parsed = urllib.parse.urlparse(self.rkn_registry_url)
            params = urllib.parse.parse_qs(parsed.query)
            if "id" in params and params["id"]:
                return params["id"][0].strip()
        except Exception:
            pass
        match = re.search(r'(\d{2}-\d{2}-\d+)', self.rkn_registry_url)
        if match:
            return match.group(1)
        match = re.search(r'[?&]id=([^&#]+)', self.rkn_registry_url)
        if match:
            return match.group(1)
        return ""

    def save(self, *args, **kwargs):
        """Обеспечивает только одну запись (singleton pattern) и оптимизацию изображений в WebP."""
        self.pk = 1
        if self.rkn_registry_url and not self.rkn_registry_number:
            self.rkn_registry_number = self.extract_rkn_number()
        from ..catalog.image_utils import optimize_image_to_webp
        if self.hero_image_top:
            optimize_image_to_webp(self.hero_image_top, max_size=1920, quality=82)
        if self.hero_image_top_mobile:
            optimize_image_to_webp(self.hero_image_top_mobile, max_size=1200, quality=82)
        if self.hero_image_bottom:
            optimize_image_to_webp(self.hero_image_bottom, max_size=1920, quality=82)
        if self.og_image:
            optimize_image_to_webp(self.og_image, max_size=1200, quality=85)
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


class PrivacyPolicy(models.Model):
    """
    Политика конфиденциальности сервиса (Singleton).
    Позволяет загрузить файл документа (.docx, .pdf, .md, .html, .txt),
    который автоматически преобразуется в чистый семантический HTML
    для нативного отображения на сайте.
    """
    title = models.CharField(
        max_length=255,
        default="Политика конфиденциальности",
        verbose_name="Заголовок страницы",
        help_text="Отображается в заголовке H1 и хлебных крошках страницы.",
    )
    file = models.FileField(
        upload_to="documents/",
        blank=True,
        null=True,
        verbose_name="Файл документа (.docx, .pdf, .md, .html, .txt)",
        help_text="Загрузите файл документа. При сохранении его содержимое автоматически конвертируется в HTML для отображения на сайте.",
    )
    content_html = models.TextField(
        blank=True,
        default="",
        verbose_name="HTML-содержимое",
        help_text="Сгенерированный HTML-код политики. Можно также редактировать напрямую вручную.",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Политика конфиденциальности"
        verbose_name_plural = "Политика конфиденциальности"

    def __str__(self):
        return self.title or "Политика конфиденциальности"

    def save(self, *args, **kwargs):
        self.pk = 1
        if self.file and not self.content_html:
            try:
                from .doc_converter import convert_document_to_html
                self.content_html = convert_document_to_html(self.file)
            except Exception:
                pass
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "title": "Политика конфиденциальности",
                "content_html": "",
            },
        )
        return obj


class LegalDocument(models.Model):
    """
    Правовой документ компании (Политика конфиденциальности, Пользовательское соглашение, Публичная оферта).
    Позволяет загрузить файл документа (.docx, .pdf, .md, .html, .txt),
    который автоматически преобразуется в чистый семантический HTML
    для нативного отображения на сайте.
    """
    DOCUMENT_CHOICES = [
        ("privacy-policy", "Политика конфиденциальности"),
        ("user-agreement", "Пользовательское соглашение"),
        ("public-offer", "Публичная оферта"),
    ]

    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="Тип / URL (slug)",
        help_text="Определяет адрес страницы на сайте (например: privacy-policy, user-agreement, public-offer)",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Заголовок страницы",
        help_text="Отображается в заголовке H1 и хлебных крошках страницы.",
    )
    file = models.FileField(
        upload_to="documents/",
        blank=True,
        null=True,
        verbose_name="Файл документа (.docx, .pdf, .md, .html, .txt)",
        help_text="Загрузите файл документа. При сохранении его содержимое автоматически конвертируется в HTML для отображения на сайте.",
    )
    content_html = models.TextField(
        blank=True,
        default="",
        verbose_name="HTML-содержимое",
        help_text="Сгенерированный HTML-код документа. Можно также редактировать напрямую вручную.",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Правовой документ"
        verbose_name_plural = "Правовые документы"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title or self.slug

    def save(self, *args, **kwargs):
        if self.file and not self.content_html:
            try:
                from .doc_converter import convert_document_to_html
                self.content_html = convert_document_to_html(self.file)
            except Exception:
                pass
        super().save(*args, **kwargs)

    @classmethod
    def get_document(cls, slug: str):
        title_map = dict(cls.DOCUMENT_CHOICES)
        default_title = title_map.get(slug, slug.replace("-", " ").capitalize())
        doc, _ = cls.objects.get_or_create(
            slug=slug,
            defaults={
                "title": default_title,
                "content_html": "",
            },
        )
        return doc


