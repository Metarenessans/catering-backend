import os
import logging
import threading
import time
from django.core.mail import send_mail
from django.conf import settings
from .telegram import format_russian_date_and_days, get_social_links_str

logger = logging.getLogger(__name__)

def _send_to_email(subject, message):
    from .models import EmailSubscriber
    try:
        active_subs = EmailSubscriber.objects.filter(is_active=True)
        recipient_list = [sub.email for sub in active_subs]
    except Exception as e:
        logger.error(f"Failed to read EmailSubscriber list from database: {e}")
        return

    if not recipient_list:
        logger.warning("No email addresses found for notifications.")
        return

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

    from_email = os.getenv('DEFAULT_FROM_EMAIL', getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'))

    try:
        send_mail(
            subject=subject,
            message=message, # Plain text fallback
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
            html_message=html_message
        )
    except Exception as e:
        logger.error(f"Failed to send email notification to {recipient_list}: {e}")

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
        
        social_links_str = get_social_links_str(phone)
        
        # Format phone and guests with <code> tag for single-tap copy
        phone_formatted = f"<code>{phone}</code>" if phone != "—" else "—"
        guests_formatted = f"<code>{guests}</code>" if guests != "—" else "—"
        
        # Format links to be on the next line
        cart_line = f"Корзина:\n{cart_link}" if cart_link != "—" else "Корзина: —"
        admin_line = f"Заявка в админке: <a href=\"{admin_link}\">открыть</a>"
        
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
            f"{social_links_str}"
        )
        
        _send_to_email("Новый заказ", message)
    except Exception as e:
        logger.error(f"Error in background order email notification for ID {order_id}: {e}")

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
                                service_lines.append(f"— {s.label} (<a href=\"{prod_url}\">привязанный товар</a>)")
                            else:
                                service_lines.append(f"— {s.label}")
                        services_str = "\n" + "\n".join(service_lines)
            except Exception as e:
                logger.error(f"Error fetching additional services for email notification: {e}")
        
        admin_link = f"{admin_base_url}/admin/menu_requests/menurequest/{menu_request.id}/change/"
        
        social_links_str = get_social_links_str(phone)
        
        # Format phone and guests with <code> tag for single-tap copy
        phone_formatted = f"<code>{phone}</code>" if phone != "—" else "—"
        guests_formatted = f"<code>{guests}</code>" if guests != "—" else "—"
        
        admin_line = f"Заявка в админке: <a href=\"{admin_link}\">открыть</a>"
        
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
            f"{social_links_str}"
        )
        
        _send_to_email("Новая заявка на подбор меню", message)
    except Exception as e:
        logger.error(f"Error in background menu request email notification for ID {menu_request_id}: {e}")

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
