import logging
import threading
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MenuRequest
from ..orders.telegram import send_menu_request_telegram_notification
from ..orders.email import send_menu_request_email_notification

logger = logging.getLogger(__name__)


@receiver(post_save, sender=MenuRequest)
def menu_request_post_save(sender, instance, created, **kwargs):
    if not created:
        return

    menu_request_id = instance.id

    def run_notifications():
        tg_thread = threading.Thread(
            target=_safe_send_tg,
            args=(instance,),
            daemon=True,
        )
        email_thread = threading.Thread(
            target=_safe_send_email,
            args=(instance,),
            daemon=True,
        )
        tg_thread.start()
        email_thread.start()

    threading.Thread(target=run_notifications, daemon=True).start()


def _safe_send_tg(instance):
    try:
        send_menu_request_telegram_notification(instance)
    except Exception as e:
        logger.error(f"Failed to trigger Telegram notification for menu request {instance.id}: {e}")


def _safe_send_email(instance):
    try:
        send_menu_request_email_notification(instance)
    except Exception as e:
        logger.error(f"Failed to trigger Email notification for menu request {instance.id}: {e}")

from django.db.models.signals import post_delete
from .models import CalculatePageSettings, CalculateFAQ
from ..catalog.revalidate import notify_frontend_revalidate


from .models import (
    CalculateFeature,
    CalculateBudgetOption,
    CalculateFoodOption,
    CalculateStep,
    AdditionalService,
)

CALCULATE_MODELS = (
    CalculatePageSettings,
    CalculateFeature,
    CalculateBudgetOption,
    CalculateFoodOption,
    CalculateStep,
    CalculateFAQ,
    AdditionalService,
)

for model_cls in CALCULATE_MODELS:
    @receiver(post_save, sender=model_cls)
    def calculate_model_post_save(sender, instance, **kwargs):
        notify_frontend_revalidate("calculate", "")

    @receiver(post_delete, sender=model_cls)
    def calculate_model_post_delete(sender, instance, **kwargs):
        notify_frontend_revalidate("calculate", "")
