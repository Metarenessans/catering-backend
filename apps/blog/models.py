import re
from django.db import models
from django.utils import timezone
from apps.catalog.models import slugify_ru


class BlogArticle(models.Model):
    title = models.CharField("Заголовок статьи", max_length=255)
    slug = models.SlugField(
        "URL-слаг",
        max_length=255,
        unique=True,
        blank=True,
        help_text="Если не заполнено, генерируется автоматически из заголовка",
    )
    cover = models.ImageField("Обложка", upload_to="blog/covers/", blank=True, null=True)
    is_cover_like_block_image = models.BooleanField(
        "Сделать обложку как картинку из блока статьи", default=False
    )
    cover_alt = models.CharField("Alt-текст обложки", max_length=255, blank=True, null=True)
    cover_source_link = models.CharField(
        "Ссылка на источник обложки", max_length=500, blank=True, null=True
    )
    created_date = models.DateField("Дата публикации", default=timezone.now)
    is_published = models.BooleanField("Опубликовано", default=True)
    seo_title = models.CharField("SEO Title", max_length=255, blank=True, null=True)
    seo_description = models.TextField("SEO Description", blank=True, null=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Статья блога"
        verbose_name_plural = "Статьи блога"
        ordering = ["-created_date", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify_ru(self.title) or "article"
            slug = base_slug
            counter = 1
            while BlogArticle.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class BlogArticleBlock(models.Model):
    article = models.ForeignKey(
        BlogArticle, on_delete=models.CASCADE, related_name="blocks", verbose_name="Статья"
    )
    image = models.ImageField(
        "Изображение в статье", upload_to="blog/images/", blank=True, null=True
    )
    image_alt = models.CharField("Alt-текст изображения", max_length=255, blank=True, null=True)
    image_source_link = models.CharField(
        "Ссылка на источник изображения", max_length=500, blank=True, null=True
    )
    image_height_unlimited = models.BooleanField("Не ограничивать по высоте", default=False)
    text = models.TextField(
        "Текст блока",
        blank=True,
        help_text=(
            "Инструкция по форматированию текста:<br/>"
            "• <b>Заголовок блока</b>: выделите строку одной звездочкой с двух сторон. Пример: <code>*Введение*</code><br/>"
            "• <b>Акцентный блок (карточка)</b>: выделите текст двумя звездочками с двух сторон. Пример:<br/>"
            "<code>**Это важный текст<br/>на две строки**</code><br/>"
            "• <b>Жирный текст</b>: выделите текст двумя символами подчёркивания с двух сторон. Пример: <code>__это жирный текст__</code><br/>"
            "• <b>Ссылки</b>: используйте стандартный HTML-тег ссылки. Пример: <code>&lt;a href=\"https://...\" target=\"_blank\"&gt;Текст&lt;/a&gt;</code><br/>"
            "• <b>Списки</b>: начните строку с символов '&gt;1. ', '&gt;2. ' и т.д. Пример:<br/>"
            "<code>&gt;1. Первый пункт<br/>&gt;2. Второй пункт</code><br/>"
            "• <b>Обычный текст</b>: пишется без специальных символов. Пустые строки создают абзацные отступы."
        ),
    )
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Блок статьи"
        verbose_name_plural = "Блоки статьи"
        ordering = ["order"]

    def __str__(self):
        if self.text:
            return f"Текст: {self.text[:50]}..."
        if self.image:
            return f"Изображение: {self.image.name}"
        return f"Блок #{self.order}"


class RelatedArticle(models.Model):
    article = models.ForeignKey(
        BlogArticle,
        on_delete=models.CASCADE,
        related_name="related_articles_association",
        verbose_name="Статья",
    )
    related_article = models.ForeignKey(
        BlogArticle, on_delete=models.CASCADE, verbose_name="Связанная статья"
    )
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Связанная статья"
        verbose_name_plural = "Связанные статьи"
        ordering = ["order"]

    def __str__(self):
        return f"{self.article.title} -> {self.related_article.title}"


class ArticleProduct(models.Model):
    article = models.ForeignKey(
        BlogArticle,
        on_delete=models.CASCADE,
        related_name="article_products",
        verbose_name="Статья",
    )
    product = models.ForeignKey(
        "catalog.Product", on_delete=models.CASCADE, verbose_name="Связанный товар / сет"
    )
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Товар из статьи"
        verbose_name_plural = "Товары из статьи"
        ordering = ["order"]

    def __str__(self):
        return f"{self.article.title} - {self.product.name}"
