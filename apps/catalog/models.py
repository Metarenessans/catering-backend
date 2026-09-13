import re
from django.db import models


def slugify_ru(text: str) -> str:
    """Транслитерация кириллицы в slug (латиницу)."""
    if not text:
        return ""
    ru_map = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo", "ж": "zh",
        "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
        "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh", "ц": "ts",
        "ч": "ch", "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu",
        "я": "ya",
    }
    transliterated = "".join(ru_map.get(char, char) for char in text.lower())
    cleaned = re.sub(r"[^a-z0-9]+", "-", transliterated)
    return cleaned.strip("-")


class Section(models.Model):
    """
    Раздел каталога (например: Фуршет, Банкет, Детское меню).
    Содержит в себе категории (связь ManyToMany).
    """
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name="Идентификатор (slug)",
        help_text="Используется как фильтр раздела (например: furshet, banquet). Если оставить пустым, сгенерируется из названия.",
    )
    name = models.CharField(max_length=200, verbose_name="Название")
    categories = models.ManyToManyField(
        "Category",
        through="SectionCategory",
        blank=True,
        related_name="sections",
        verbose_name="Категории",
        help_text="Выберите категории, входящие в этот раздел",
    )
    image_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="URL изображения (внешний)",
    )
    image = models.ImageField(
        upload_to="sections/",
        null=True,
        blank=True,
        verbose_name="Изображение (загружаемое)",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    seo_title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="SEO Заголовок (Title)",
        help_text="Оставьте пустым для автогенерации (например: Фуршетные блюда и закуски — заказать с доставкой в Набережных Челнах)",
    )
    seo_description = models.TextField(
        blank=True,
        default="",
        verbose_name="SEO Описание (Description)",
        help_text="Оставьте пустым для автогенерации по формуле с перечислением категорий раздела",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Раздел"
        verbose_name_plural = "Разделы"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify_ru(self.name) or "section"
            slug = base_slug
            counter = 1
            while Section.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def effective_image_url(self):
        """Возвращает URL изображения: сначала загруженное, затем внешнее."""
        if self.image:
            url = self.image.url
            from django.conf import settings
            import os
            try:
                if settings.DEBUG and not os.path.exists(self.image.path):
                    return f"https://chefmil-furshet.ru{url}"
            except ValueError:
                pass
            return url
        return self.image_url


class Category(models.Model):
    """
    Категория продуктов.
    Соответствует categoriesData из frontend/src/mock-data.ts.
    """
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name="Идентификатор (slug)",
        help_text="Используется как фильтр в каталоге (например: profitable, desserts). Если оставить пустым, сгенерируется из названия.",
    )
    name = models.CharField(max_length=200, verbose_name="Название")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify_ru(self.name) or "category"
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class SectionCategory(models.Model):
    """
    Промежуточная модель связи Раздел — Категория.
    Позволяет настраивать порядок отображения категорий индивидуально для каждого раздела.
    """
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="section_categories",
        verbose_name="Раздел",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="category_sections",
        verbose_name="Категория",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок сортировки",
        db_index=True,
    )

    class Meta:
        verbose_name = "Категория раздела"
        verbose_name_plural = "Категории раздела"
        ordering = ["order", "id"]
        unique_together = [("section", "category")]

    def __str__(self):
        return f"{self.section.name} — {self.category.name}"


class ProductExtraInfo(models.Model):
    """
    Дополнительная информация о продукте (количество/вес).
    Соответствует extraInfo: { amount: number; unit: string }[] из frontend.
    """
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="extra_info",
        verbose_name="Продукт",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Количество/вес",
    )
    unit = models.CharField(max_length=50, verbose_name="Единица измерения")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Доп. информация"
        verbose_name_plural = "Доп. информация"
        ordering = ["order"]

    def __str__(self):
        return f"{self.amount} {self.unit}"


class Product(models.Model):
    """
    Продукт (блюдо/набор) каталога.
    Соответствует интерфейсу Product из frontend/src/mock-data.ts.
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="Категория",
    )
    slug = models.SlugField(
        max_length=300,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Идентификатор (slug)",
        help_text="Используется в URL карточки товара. Если оставить пустым, сгенерируется из названия.",
    )
    name = models.CharField(max_length=300, verbose_name="Название")
    image_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="URL изображения (внешний)",
    )
    image = models.ImageField(
        upload_to="products/",
        null=True,
        blank=True,
        verbose_name="Изображение (загружаемое)",
    )
    description = models.TextField(blank=True, default="", verbose_name="Описание")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена (₽)",
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Старая цена (₽)",
        help_text="Заполните, если хотите показать зачёркнутую цену",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Рекомендуемый",
        help_text="Отображается в разделе 'Выгодно'",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    min_order_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Минимальное количество заказа",
        help_text="Минимальное количество товара для заказа. Если пусто, ограничений нет.",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify_ru(self.name)[:280] or "product"
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def effective_image_url(self):
        """Возвращает URL изображения: сначала загруженное, затем внешнее."""
        if self.image:
            url = self.image.url
            from django.conf import settings
            import os
            try:
                if settings.DEBUG and not os.path.exists(self.image.path):
                    return f"https://chefmil-furshet.ru{url}"
            except ValueError:
                pass
            return url
        return self.image_url


class ProductOption(models.Model):
    """
    Вариант цены/наполнения для карточки товара (например, 10, 20, 30, 50 персон).
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="options",
        verbose_name="Продукт",
    )
    name = models.CharField(max_length=200, verbose_name="Название варианта")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена варианта (₽)",
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Старая цена варианта (₽)",
    )
    min_order_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Минимальное количество заказа",
        help_text="Минимальное количество товара для заказа этого варианта. Если пусто, используется ограничение продукта.",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Вариант товара"
        verbose_name_plural = "Варианты товара"
        ordering = ["order"]

    def __str__(self):
        return f"{self.product.name} - {self.name} ({self.price} ₽)"
