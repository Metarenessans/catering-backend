from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, Section, Category
from .revalidate import notify_frontend_revalidate


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
