from django.db import models


class Category(models.Model):
    """
    Категория продуктов.
    Соответствует categoriesData из frontend/src/mock-data.ts.
    """
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="Идентификатор (slug)",
        help_text="Используется как фильтр в каталоге (например: profitable, desserts)",
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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    @property
    def effective_image_url(self):
        """Возвращает URL изображения: сначала загруженное, затем внешнее."""
        if self.image:
            return self.image.url
        return self.image_url
