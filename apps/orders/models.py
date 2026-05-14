from django.db import models
from ..catalog.models import Product


class Order(models.Model):
    """
    Заказ, оформленный через корзину (CartModal).

    Константы из frontend:
      MIN_ORDER = 5000 ₽ — минимальная сумма заказа
      DELIVERY_THRESHOLD = 10000 ₽ — порог бесплатной доставки
      DELIVERY_COST = 1500 ₽ — стоимость платной доставки
    """

    class StatusChoices(models.TextChoices):
        NEW = "new", "Новый"
        CONFIRMED = "confirmed", "Подтверждён"
        IN_PROGRESS = "in_progress", "В работе"
        DELIVERED = "delivered", "Доставлен"
        COMPLETED = "completed", "Выполнен"
        CANCELLED = "cancelled", "Отменён"

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.NEW,
        verbose_name="Статус",
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Сумма позиций (₽)",
    )
    delivery_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Стоимость доставки (₽)",
    )
    final_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Итоговая сумма (₽)",
    )
    comment = models.TextField(blank=True, default="", verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ №{self.pk} — {self.final_price} ₽ ({self.get_status_display()})"


class OrderItem(models.Model):
    """
    Позиция заказа — снимок продукта на момент оформления.
    Цена и название фиксируются, чтобы изменение каталога не влияло на историю.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Продукт (ссылка)",
    )
    # Snapshot fields — зафиксированные данные на момент заказа
    product_name = models.CharField(max_length=300, verbose_name="Название (снимок)")
    product_image_url = models.URLField(
        max_length=500, blank=True, default="", verbose_name="URL изображения (снимок)"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена за ед. (₽)"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    subtotal = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Сумма (₽)"
    )

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)
