from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import BlogArticle, BlogArticleBlock
from apps.catalog.image_utils import optimize_image_to_webp
from apps.catalog.revalidate import notify_frontend_revalidate


@receiver(pre_save, sender=BlogArticle)
def blog_article_before_save(sender, instance, **kwargs):
    if instance.cover:
        optimize_image_to_webp(instance.cover, max_size=1920, quality=82)


@receiver(pre_save, sender=BlogArticleBlock)
def blog_article_block_before_save(sender, instance, **kwargs):
    if instance.image:
        optimize_image_to_webp(instance.image, max_size=1600, quality=82)


@receiver(post_save, sender=BlogArticle)
@receiver(post_delete, sender=BlogArticle)
def blog_article_changed(sender, instance, **kwargs):
    slug = instance.slug or str(instance.id)
    notify_frontend_revalidate("blog", slug)
