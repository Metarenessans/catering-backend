import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .telegram import send_order_telegram_notification
from .email import send_order_email_notification

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def order_post_save(sender, instance, created, **kwargs):
    if created:
        try:
            send_order_telegram_notification(instance)
        except Exception as e:
            logger.error(f"Failed to trigger Telegram notification for order {instance.id}: {e}")
        try:
            send_order_email_notification(instance)
        except Exception as e:
            logger.error(f"Failed to trigger Email notification for order {instance.id}: {e}")
