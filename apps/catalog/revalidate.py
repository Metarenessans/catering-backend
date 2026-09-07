import json
import logging
import threading
import urllib.request
from django.conf import settings

logger = logging.getLogger(__name__)


def notify_frontend_revalidate(event_type: str = "all", slug: str = ""):
    """
    Отправляет асинхронный webhook на фронтенд Next.js
    для ленивого сброса кэша микроразметки и страниц.
    Выполняется в фоновом daemon-потоке, не блокируя сохранение в админке Django.
    """
    def _send():
        try:
            from apps.system_settings.models import SystemSettings
            sys_settings = SystemSettings.load()
            frontend_url = sys_settings.get_frontend_url()
            secret = sys_settings.get_revalidation_secret()
            url = f"{frontend_url}/api/revalidate-schema"

            payload = json.dumps({
                "secret": secret,
                "type": event_type,
                "slug": slug,
            }).encode("utf-8")

            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    logger.info(f"Frontend revalidation triggered successfully for {event_type}:{slug}")
                else:
                    logger.warning(f"Frontend revalidation returned status {resp.status}")
        except Exception as e:
            # Не бросаем ошибку наружу, чтобы сбой сети с фронтендом никогда не ломал работу админки Django
            logger.warning(f"Could not notify frontend about revalidation ({event_type}:{slug}): {e}")

    threading.Thread(target=_send, daemon=True).start()
