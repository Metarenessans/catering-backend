from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import Product, Section, Category
from .revalidate import notify_frontend_revalidate
from .image_utils import optimize_image_to_webp


@receiver(pre_save, sender=Product)
def product_before_save(sender, instance, **kwargs):
    if instance.image:
        optimize_image_to_webp(instance.image, max_size=1600, quality=82)


@receiver(pre_save, sender=Section)
def section_before_save(sender, instance, **kwargs):
    if instance.image:
        optimize_image_to_webp(instance.image, max_size=1600, quality=82)


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def product_changed(sender, instance, **kwargs):
    slug = instance.slug or str(instance.id)
    notify_frontend_revalidate("product", slug)


@receiver(post_save, sender=Section)
@receiver(post_delete, sender=Section)
def section_changed(sender, instance, **kwargs):
    slug = instance.slug or str(instance.id)
    notify_frontend_revalidate("section", slug)


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def category_changed(sender, instance, **kwargs):
    notify_frontend_revalidate("category", instance.slug)

