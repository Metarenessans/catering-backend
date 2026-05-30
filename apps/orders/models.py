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
    name = models.CharField(
        max_length=200,
        default="",
        blank=True,
        verbose_name="Имя клиента",
    )
    phone = models.CharField(
        max_length=30,
        default="",
        blank=True,
        verbose_name="Телефон",
    )
    contact_method = models.CharField(
        max_length=50,
        default="Позвонить мне",
        verbose_name="Способ связи",
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
    guests = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Количество гостей",
    )
    event_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата мероприятия",
    )
    comment = models.TextField(blank=True, default="", verbose_name="Комментарий")
    cart_link = models.URLField(
        max_length=3000,
        blank=True,
        default="",
        verbose_name="Ссылка на корзину",
    )
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


class TelegramSubscriber(models.Model):
    username = models.CharField(
        max_length=150,
        blank=True,
        default="",
        verbose_name="Username в Telegram",
        help_text="Без символа @. Например: ivan_manager",
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        default="",
        verbose_name="Номер телефона",
        help_text="Например: +79991234567",
    )
    chat_id = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Telegram Chat ID",
        help_text="Заполняется автоматически при подключении пользователя в боте",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Если снято, пользователь перестанет получать уведомления",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Подписчик Telegram"
        verbose_name_plural = "Подписчики Telegram"

    def __str__(self):
        identifiers = []
        if self.username:
            identifiers.append(f"@{self.username}")
        if self.phone:
            identifiers.append(self.phone)
        ident_str = " / ".join(identifiers) or "Без идентификатора"
        
        status = "активен" if self.is_active else "заблокирован"
        connected = "подключен" if self.chat_id else "ожидает подключения"
        return f"{ident_str} ({status}, {connected})"


class EmailSubscriber(models.Model):
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Адрес электронной почты для получения уведомлений",
    )
    name = models.CharField(
        max_length=150,
        blank=True,
        default="",
        verbose_name="Имя владельца",
        help_text="Опционально (например: Менеджер Иван)",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Если снято, на этот адрес не будут приходить уведомления",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Подписчик Email"
        verbose_name_plural = "Подписчики Email"

    def __str__(self):
        status = "активен" if self.is_active else "отключен"
        if self.name:
            return f"{self.name} <{self.email}> ({status})"
        return f"{self.email} ({status})"
