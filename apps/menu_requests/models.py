from django.db import models


class AdditionalService(models.Model):
    """
    Дополнительная услуга для подбора меню.
    Соответствует additionalOptions из menu-popup.tsx.
    """
    label = models.CharField(max_length=200, verbose_name="Название услуги")
    description = models.TextField(blank=True, default="", verbose_name="Описание")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Доп. услуга"
        verbose_name_plural = "Доп. услуги"
        ordering = ["order"]

    def __str__(self):
        return self.label


class EventFormat(models.Model):
    """
    Формат мероприятия.
    Соответствует массиву formats из menu-popup.tsx.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Формат мероприятия"
        verbose_name_plural = "Форматы мероприятий"
        ordering = ["order"]

    def __str__(self):
        return self.name


class MenuRequest(models.Model):
    """
    Заявка на подбор меню — отправляется из MenuPopup.
    Соответствует интерфейсу MenuFormData из frontend.
    """

    class StatusChoices(models.TextChoices):
        NEW = "new", "Новая"
        PROCESSING = "processing", "В обработке"
        DONE = "done", "Выполнена"
        CANCELLED = "cancelled", "Отменена"

    # Step 1 fields
    format = models.CharField(max_length=100, verbose_name="Формат мероприятия")
    guests = models.PositiveIntegerField(verbose_name="Количество гостей")
    date = models.DateField(verbose_name="Дата мероприятия")
    food_preferences = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Предпочтения по блюдам",
        help_text='Список строк: ["Супы, бульоны", "Горячее", ...]',
    )

    # Step 2 fields
    additional_services = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Дополнительные услуги",
        help_text='Список ID услуг: ["1", "2", ...]',
    )
    name = models.CharField(max_length=200, verbose_name="Имя клиента")
    phone = models.CharField(max_length=30, verbose_name="Телефон")
    consent = models.BooleanField(default=True, verbose_name="Согласие с политикой")

    # Meta
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.NEW,
        verbose_name="Статус",
    )
    notes = models.TextField(blank=True, default="", verbose_name="Заметки менеджера")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Заявка на меню"
        verbose_name_plural = "Заявки на меню"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заявка №{self.pk} — {self.name} ({self.format}, {self.date})"
