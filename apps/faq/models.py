from django.db import models


class FaqItem(models.Model):
    """
    Элемент FAQ.
    Соответствует интерфейсу FaqItem из frontend/src/mock-data.ts.
    """
    question = models.CharField(max_length=300, verbose_name="Вопрос")
    answer_items = models.JSONField(
        default=list,
        verbose_name="Ответы",
        help_text='Список строк: ["ответ 1", "ответ 2", ...]',
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Вопрос FAQ"
        verbose_name_plural = "FAQ"
        ordering = ["order"]

    def __str__(self):
        return self.question
