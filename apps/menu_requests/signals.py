import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MenuRequest
from ..orders.telegram import send_menu_request_telegram_notification

logger = logging.getLogger(__name__)

@receiver(post_save, sender=MenuRequest)
def menu_request_post_save(sender, instance, created, **kwargs):
    if created:
        try:
            send_menu_request_telegram_notification(instance)
        except Exception as e:
            logger.error(f"Failed to trigger Telegram notification for menu request {instance.id}: {e}")
