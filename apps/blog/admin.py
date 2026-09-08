from django.contrib import admin
from adminsortable2.admin import (
    SortableAdminBase,
    SortableStackedInline,
    SortableTabularInline,
)
from .models import BlogArticle, BlogArticleBlock, RelatedArticle, ArticleProduct


class BlogArticleBlockInline(SortableStackedInline):
    model = BlogArticleBlock
    extra = 0
    fields = (
        "order",
        "text",
        "image",
        "image_height_unlimited",
        "image_alt",
        "image_source_link",
    )


class RelatedArticleInline(SortableTabularInline):
    model = RelatedArticle
    extra = 1
    fk_name = "article"
    fields = ("order", "related_article")
    verbose_name = "Связанная статья"
    verbose_name_plural = "Связанные статьи"


class ArticleProductInline(SortableTabularInline):
    model = ArticleProduct
    extra = 1
    fk_name = "article"
    fields = ("order", "product")
    verbose_name = "Товар / сет из статьи"
    verbose_name_plural = "Товары / сеты из статьи"
    autocomplete_fields = ("product",)


@admin.register(BlogArticle)
class BlogArticleAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ("title", "slug", "created_date", "is_published", "created_at")
    list_filter = ("is_published", "created_date")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (BlogArticleBlockInline, RelatedArticleInline, ArticleProductInline)
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "title",
                    "slug",
                    "created_date",
                    "is_published",
                    "cover",
                    "is_cover_like_block_image",
                    "cover_alt",
                    "cover_source_link",
                ),
            },
        ),
        (
            "SEO настройки",
            {
                "fields": ("seo_title", "seo_description"),
            },
        ),
    )
