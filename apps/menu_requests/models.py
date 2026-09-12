from django.db import models
from ..catalog.models import Product


class CalculatePageSettings(models.Model):
    """
    Настройки страницы расчёта меню (/calculate) — Единственная запись (Singleton).
    """
    # 1. Хиро-секция
    hero_badge = models.CharField(
        max_length=150,
        default="⚡ Бесплатный расчет за 15 минут",
        verbose_name="Бейдж в шапке",
        help_text="Короткий бейдж над заголовком",
    )
    hero_title = models.CharField(
        max_length=255,
        default="Рассчитать меню кейтеринга и банкета в Набережных Челнах",
        verbose_name="Заголовок страницы (H1)",
    )
    hero_description = models.TextField(
        default="Укажите формат события, количество персон и пожелания - бесплатно составим персональное меню и смету под ваш бюджет.",
        verbose_name="Подзаголовок / описание страницы",
    )

    # 2. Секция "Как мы работаем"
    steps_title = models.CharField(
        max_length=150,
        default="Как мы работаем",
        verbose_name="Заголовок блока шагов",
    )
    steps_subtitle = models.CharField(
        max_length=255,
        default="Прозрачный и комфортный процесс подготовки вашего праздничного стола",
        verbose_name="Подзаголовок блока шагов",
    )

    # 3. Секция FAQ
    faq_title = models.CharField(
        max_length=150,
        default="Часто задаваемые вопросы о расчете меню",
        verbose_name="Заголовок блока FAQ",
    )
    faq_subtitle = models.CharField(
        max_length=255,
        default="Ответы на популярные вопросы о подборе блюд, сроках и сервировке",
        verbose_name="Подзаголовок блока FAQ",
    )

    # 4. SEO мета-теги
    seo_title = models.CharField(
        max_length=255,
        blank=True,
        default="Рассчитать меню кейтеринга онлайн - Бесплатный расчет банкета и фуршета | Шеф Мил",
        verbose_name="SEO Заголовок (Meta Title)",
        help_text="Оставьте пустым для значения по умолчанию",
    )
    seo_description = models.TextField(
        blank=True,
        default="Бесплатный онлайн-расчёт меню кейтеринга под формат мероприятия, количество гостей и бюджет в Набережных Челнах. Персональная смета за 15 минут!",
        verbose_name="SEO Описание (Meta Description)",
        help_text="Оставьте пустым для значения по умолчанию",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Настройка страницы расчёта"
        verbose_name_plural = "Настройка страницы расчёта"

    def __str__(self):
        return "Настройка страницы расчёта"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AdditionalService(models.Model):
    """
    Дополнительная услуга для подбора меню.
    Управляется внутри настроек страницы расчёта.
    """
    settings = models.ForeignKey(
        CalculatePageSettings,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=1,
        related_name="additional_services",
        verbose_name="Настройки страницы",
    )
    label = models.CharField(max_length=200, verbose_name="Название услуги")
    description = models.TextField(blank=True, default="", verbose_name="Описание")
    linked_product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_services",
        verbose_name="Связанный товар",
        help_text="Товар, который откроется при клике на 'узнать подробнее'"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Доп. услуга"
        verbose_name_plural = "Дополнительные услуги"
        ordering = ["order"]

    def __str__(self):
        return self.label


class CalculateFeature(models.Model):
    """
    Преимущество (3 карточки под хиро-секцией).
    """
    settings = models.ForeignKey(
        CalculatePageSettings,
        on_delete=models.CASCADE,
        related_name="features",
        default=1,
        verbose_name="Настройки страницы",
    )
    icon = models.CharField(max_length=20, default="⏱️", verbose_name="Иконка / Эмодзи")
    title = models.CharField(max_length=150, verbose_name="Заголовок")
    subtitle = models.CharField(max_length=255, verbose_name="Подзаголовок")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Преимущество"
        verbose_name_plural = "Преимущества (карточки под хиро)"
        ordering = ["order"]

    def __str__(self):
        return f"{self.icon} {self.title}"


class CalculateBudgetOption(models.Model):
    """
    Опция примерного бюджета для формы расчёта.
    """
    settings = models.ForeignKey(
        CalculatePageSettings,
        on_delete=models.CASCADE,
        related_name="budget_options",
        default=1,
        verbose_name="Настройки страницы",
    )
    name = models.CharField(max_length=150, verbose_name="Опция бюджета")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Опция бюджета"
        verbose_name_plural = "Опции примерного бюджета"
        ordering = ["order"]

    def __str__(self):
        return self.name


class CalculateFoodOption(models.Model):
    """
    Опция вида блюда (предпочтения по кухне).
    """
    settings = models.ForeignKey(
        CalculatePageSettings,
        on_delete=models.CASCADE,
        related_name="food_options",
        default=1,
        verbose_name="Настройки страницы",
    )
    name = models.CharField(max_length=150, verbose_name="Вид блюда")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Вид блюда"
        verbose_name_plural = "Виды блюд (предпочтения)"
        ordering = ["order"]

    def __str__(self):
        return self.name


class CalculateStep(models.Model):
    """
    Шаг процесса («Как мы работаем»).
    """
    settings = models.ForeignKey(
        CalculatePageSettings,
        on_delete=models.CASCADE,
        related_name="steps",
        default=1,
        verbose_name="Настройки страницы",
    )
    step = models.CharField(max_length=10, default="01", verbose_name="Номер шага (01, 02...)")
    title = models.CharField(max_length=150, verbose_name="Заголовок шага")
    text = models.TextField(verbose_name="Описание шага")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Шаг процесса"
        verbose_name_plural = "Шаги процесса («Как мы работаем»)"
        ordering = ["order"]

    def __str__(self):
        return f"{self.step} {self.title}"


class CalculateFAQ(models.Model):
    """
    Вопрос и ответ FAQ для страницы расчёта меню.
    """
    settings = models.ForeignKey(
        CalculatePageSettings,
        on_delete=models.CASCADE,
        related_name="faqs",
        verbose_name="Настройки страницы",
        default=1,
    )
    question = models.CharField(max_length=300, verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Вопрос FAQ"
        verbose_name_plural = "Вопросы FAQ"
        ordering = ["order"]

    def __str__(self):
        return self.question


class EventFormat(models.Model):
    """
    Формат мероприятия.
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
    Заявка на расчёт меню — отправляется из формы расчёта / MenuPopup.
    """

    class StatusChoices(models.TextChoices):
        NEW = "new", "Новая"
        PROCESSING = "processing", "В обработке"
        DONE = "done", "Выполнена"
        CANCELLED = "cancelled", "Отменена"

    format = models.CharField(max_length=100, verbose_name="Формат мероприятия")
    guests = models.CharField(max_length=100, blank=True, default="", verbose_name="Количество гостей")
    budget = models.CharField(max_length=100, blank=True, default="", verbose_name="Примерный бюджет")
    date = models.DateField(null=True, blank=True, verbose_name="Дата мероприятия")
    food_preferences = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Предпочтения по блюдам",
        help_text='Список строк: ["Супы, бульоны", "Горячее", ...]',
    )

    additional_services = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Дополнительные услуги",
        help_text='Список ID услуг: ["1", "2", ...]',
    )
    name = models.CharField(max_length=200, verbose_name="Имя клиента")
    phone = models.CharField(max_length=30, verbose_name="Телефон")
    contact_method = models.CharField(
        max_length=50,
        default="Позвонить мне",
        verbose_name="Способ связи",
    )
    consent = models.BooleanField(default=True, verbose_name="Согласие с политикой")

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
        verbose_name = "Заявка на расчёт меню"
        verbose_name_plural = "Заявки на расчёт меню"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заявка №{self.pk} — {self.name} ({self.format}, {self.date})"
