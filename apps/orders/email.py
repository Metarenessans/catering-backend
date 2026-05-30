import os
import logging
import threading
import time
import re
from django.core.mail import send_mail
from django.conf import settings
from .telegram import format_russian_date_and_days

logger = logging.getLogger(__name__)


def _clean_phone_number(phone):
    if not phone:
        return ""
    digits = "".join(re.findall(r'\d', phone))
    if len(digits) == 11 and digits.startswith('8'):
        digits = '7' + digits[1:]
    return digits


def _get_contact_links_html(phone):
    """Быстро генерирует WhatsApp и Telegram ссылки без обращения к Telethon."""
    clean_phone = _clean_phone_number(phone)
    if not clean_phone:
        return "—"
    wa_link = f'<a href="https://wa.me/{clean_phone}">WhatsApp</a>'
    tg_link = f'<a href="https://t.me/+{clean_phone}">Telegram (по номеру)</a>'
    return f"{wa_link}, {tg_link}"


def _send_to_email(subject, message, raise_exception=False):
    from .models import EmailSubscriber

    # Диагностика конфигурации почты
    email_host = getattr(settings, 'EMAIL_HOST', None) or os.getenv('EMAIL_HOST')
    email_user = getattr(settings, 'EMAIL_HOST_USER', None) or os.getenv('EMAIL_HOST_USER')
    if not email_host or not email_user:
        msg = (
            "Email notification skipped: EMAIL_HOST or EMAIL_HOST_USER is not configured. "
            f"EMAIL_HOST={email_host!r}, EMAIL_HOST_USER={email_user!r}"
        )
        logger.error(msg)
        if raise_exception:
            raise ValueError(msg)
        return

    try:
        active_subs = EmailSubscriber.objects.filter(is_active=True)
        recipient_list = [sub.email for sub in active_subs]
    except Exception as e:
        msg = f"Failed to read EmailSubscriber list from database: {e}"
        logger.error(msg)
        if raise_exception:
            raise Exception(msg) from e
        return

    if not recipient_list:
        msg = "No email addresses found for notifications (EmailSubscriber table is empty or all subscribers are inactive)."
        logger.warning(msg)
        if raise_exception:
            raise ValueError(msg)
        return

    logger.info(f"Sending email '{subject}' to {recipient_list}")

    # Convert \n to <br> for HTML email formatting
    html_message = message.replace('\n', '<br>')

    # Wrap in basic HTML structure
    html_message = f"""
    <html>
    <head>
    <style>
        body {{ font-family: sans-serif; line-height: 1.5; font-size: 14px; }}
        code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 4px; }}
    </style>
    </head>
    <body>
    {html_message}
    </body>
    </html>
    """

    from_email = os.getenv('DEFAULT_FROM_EMAIL', getattr(settings, 'DEFAULT_FROM_EMAIL', email_user))

    try:
        send_mail(
            subject=subject,
            message=message,  # Plain text fallback
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
            html_message=html_message
        )
        logger.info(f"Email '{subject}' sent successfully to {recipient_list}")
    except Exception as e:
        logger.error(f"Failed to send email notification to {recipient_list}: {e}", exc_info=True)
        if raise_exception:
            raise e


def _send_order_email_notification_bg(order_id):
    """Фоновая сборка и отправка email-уведомления о заказе."""
    try:
        # Даем транзакции Django завершиться
        time.sleep(0.5)
        from .models import Order
        order = Order.objects.get(id=order_id)

        name = order.name or "—"
        phone = order.phone or "—"
        contact_method = order.contact_method or "—"
        guests = order.guests or "—"
        event_date_str = format_russian_date_and_days(order.event_date)
        cart_link = order.cart_link or "—"

        admin_base_url = os.getenv("ADMIN_BASE_URL", "https://chefmil-furshet.ru").rstrip("/")
        admin_link = f"{admin_base_url}/admin/orders/order/{order.id}/change/"

        total_price = f"{int(order.total_price)} ₽" if order.total_price is not None else "—"

        contact_links = _get_contact_links_html(phone)

        phone_formatted = f"<code>{phone}</code>" if phone != "—" else "—"
        guests_formatted = f"<code>{guests}</code>" if guests != "—" else "—"

        cart_line = f"Корзина:\n{cart_link}" if cart_link != "—" else "Корзина: —"
        admin_line = f'Заявка в админке: <a href="{admin_link}">открыть</a>'

        message = (
            f"<b>- Заказ -</b>\n\n"
            f"Имя: {name}\n"
            f"Телефон: {phone_formatted}\n"
            f"Способ связи: {contact_method}\n"
            f"Количество гостей: {guests_formatted}\n"
            f"К дате: {event_date_str}\n"
            f"{cart_line}\n"
            f"{admin_line}\n"
            f"Итого: {total_price}\n\n"
            f"Дополнительно:\n"
            f"{contact_links}"
        )

        _send_to_email("Новый заказ", message)
    except Exception as e:
        logger.error(f"Error in background order email notification for ID {order_id}: {e}", exc_info=True)


def _send_menu_request_email_notification_bg(menu_request_id):
    """Фоновая сборка и отправка email-уведомления о подборе меню."""
    try:
        # Даем транзакции Django завершиться
        time.sleep(0.5)
        from ..menu_requests.models import MenuRequest
        menu_request = MenuRequest.objects.get(id=menu_request_id)

        name = menu_request.name or "—"
        phone = menu_request.phone or "—"
        contact_method = menu_request.contact_method or "—"
        guests = menu_request.guests or "—"
        event_date_str = format_russian_date_and_days(menu_request.date)
        event_format = menu_request.format or "—"

        # Виды блюд
        food_prefs = menu_request.food_preferences or []
        if food_prefs:
            food_prefs_lines = [f"— {pref}" for pref in food_prefs]
            food_prefs_str = "\n" + "\n".join(food_prefs_lines)
        else:
            food_prefs_str = " —"

        admin_base_url = os.getenv("ADMIN_BASE_URL", "https://chefmil-furshet.ru").rstrip("/")

        # Дополнительные услуги (извлекаем по ID)
        services_str = "—"
        service_ids = menu_request.additional_services or []
        if service_ids:
            try:
                from ..menu_requests.models import AdditionalService
                int_ids = []
                for sid in service_ids:
                    try:
                        int_ids.append(int(sid))
                    except ValueError:
                        pass
                if int_ids:
                    services = AdditionalService.objects.filter(id__in=int_ids).select_related('linked_product')
                    if services.exists():
                        service_lines = []
                        for s in services:
                            if s.linked_product:
                                prod_url = f"{admin_base_url}/admin/catalog/product/{s.linked_product.id}/change/"
                                service_lines.append(f'— {s.label} (<a href="{prod_url}">привязанный товар</a>)')
                            else:
                                service_lines.append(f"— {s.label}")
                        services_str = "\n" + "\n".join(service_lines)
            except Exception as e:
                logger.error(f"Error fetching additional services for email notification: {e}")

        admin_link = f"{admin_base_url}/admin/menu_requests/menurequest/{menu_request.id}/change/"

        contact_links = _get_contact_links_html(phone)

        phone_formatted = f"<code>{phone}</code>" if phone != "—" else "—"
        guests_formatted = f"<code>{guests}</code>" if guests != "—" else "—"

        admin_line = f'Заявка в админке: <a href="{admin_link}">открыть</a>'

        message = (
            f"<b>- Подбор меню -</b>\n\n"
            f"Имя: {name}\n"
            f"Телефон: {phone_formatted}\n"
            f"Способ связи: {contact_method}\n"
            f"Формат мероприятия: {event_format}\n"
            f"Количество гостей: {guests_formatted}\n"
            f"К дате: {event_date_str}\n"
            f"Виды блюд: {food_prefs_str}\n"
            f"Доп. услуги: {services_str}\n\n"
            f"{admin_line}\n\n"
            f"Дополнительно:\n"
            f"{contact_links}"
        )

        _send_to_email("Новая заявка на подбор меню", message)
    except Exception as e:
        logger.error(f"Error in background menu request email notification for ID {menu_request_id}: {e}", exc_info=True)


def send_order_email_notification(order):
    """Sends email notification about a new order asynchronously."""
    threading.Thread(
        target=_send_order_email_notification_bg,
        args=(order.id,),
        daemon=True
    ).start()


def send_menu_request_email_notification(menu_request):
    """Sends email notification about a new menu request asynchronously."""
    threading.Thread(
        target=_send_menu_request_email_notification_bg,
        args=(menu_request.id,),
        daemon=True
    ).start()


def send_order_email_notification_sync(order_id, raise_exception=True):
    """Синхронная сборка и отправка email-уведомления о заказе."""
    from .models import Order
    order = Order.objects.get(id=order_id)

    name = order.name or "—"
    phone = order.phone or "—"
    contact_method = order.contact_method or "—"
    guests = order.guests or "—"
    event_date_str = format_russian_date_and_days(order.event_date)
    cart_link = order.cart_link or "—"

    admin_base_url = os.getenv("ADMIN_BASE_URL", "https://chefmil-furshet.ru").rstrip("/")
    admin_link = f"{admin_base_url}/admin/orders/order/{order.id}/change/"

    total_price = f"{int(order.total_price)} ₽" if order.total_price is not None else "—"

    contact_links = _get_contact_links_html(phone)

    phone_formatted = f"<code>{phone}</code>" if phone != "—" else "—"
    guests_formatted = f"<code>{guests}</code>" if guests != "—" else "—"

    cart_line = f"Корзина:\n{cart_link}" if cart_link != "—" else "Корзина: —"
    admin_line = f'Заявка в админке: <a href="{admin_link}">открыть</a>'

    message = (
        f"<b>- Заказ -</b>\n\n"
        f"Имя: {name}\n"
        f"Телефон: {phone_formatted}\n"
        f"Способ связи: {contact_method}\n"
        f"Количество гостей: {guests_formatted}\n"
        f"К дате: {event_date_str}\n"
        f"{cart_line}\n"
        f"{admin_line}\n"
        f"Итого: {total_price}\n\n"
        f"Дополнительно:\n"
        f"{contact_links}"
    )

    _send_to_email("Новый заказ", message, raise_exception=raise_exception)


def send_menu_request_email_notification_sync(menu_request_id, raise_exception=True):
    """Синхронная сборка и отправка email-уведомления о подборе меню."""
    from ..menu_requests.models import MenuRequest
    menu_request = MenuRequest.objects.get(id=menu_request_id)

    name = menu_request.name or "—"
    phone = menu_request.phone or "—"
    contact_method = menu_request.contact_method or "—"
    guests = menu_request.guests or "—"
    event_date_str = format_russian_date_and_days(menu_request.date)
    event_format = menu_request.format or "—"

    # Виды блюд
    food_prefs = menu_request.food_preferences or []
    if food_prefs:
        food_prefs_lines = [f"— {pref}" for pref in food_prefs]
        food_prefs_str = "\n" + "\n".join(food_prefs_lines)
    else:
        food_prefs_str = " —"

    admin_base_url = os.getenv("ADMIN_BASE_URL", "https://chefmil-furshet.ru").rstrip("/")

    # Дополнительные услуги (извлекаем по ID)
    services_str = "—"
    service_ids = menu_request.additional_services or []
    if service_ids:
        try:
            from ..menu_requests.models import AdditionalService
            int_ids = []
            for sid in service_ids:
                try:
                    int_ids.append(int(sid))
                except ValueError:
                    pass
            if int_ids:
                services = AdditionalService.objects.filter(id__in=int_ids).select_related('linked_product')
                if services.exists():
                    service_lines = []
                    for s in services:
                        if s.linked_product:
                            prod_url = f"{admin_base_url}/admin/catalog/product/{s.linked_product.id}/change/"
                            service_lines.append(f'— {s.label} (<a href="{prod_url}">привязанный товар</a>)')
                        else:
                            service_lines.append(f"— {s.label}")
                    services_str = "\n" + "\n".join(service_lines)
        except Exception as e:
            logger.error(f"Error fetching additional services for email notification: {e}")

    admin_link = f"{admin_base_url}/admin/menu_requests/menurequest/{menu_request.id}/change/"

    contact_links = _get_contact_links_html(phone)

    phone_formatted = f"<code>{phone}</code>" if phone != "—" else "—"
    guests_formatted = f"<code>{guests}</code>" if guests != "—" else "—"

    admin_line = f'Заявка в админке: <a href="{admin_link}">открыть</a>'

    message = (
        f"<b>- Подбор меню -</b>\n\n"
        f"Имя: {name}\n"
        f"Телефон: {phone_formatted}\n"
        f"Способ связи: {contact_method}\n"
        f"Формат мероприятия: {event_format}\n"
        f"Количество гостей: {guests_formatted}\n"
        f"К дате: {event_date_str}\n"
        f"Виды блюд: {food_prefs_str}\n"
        f"Доп. услуги: {services_str}\n\n"
        f"{admin_line}\n\n"
        f"Дополнительно:\n"
        f"{contact_links}"
    )

    _send_to_email("Новая заявка на подбор меню", message, raise_exception=raise_exception)
