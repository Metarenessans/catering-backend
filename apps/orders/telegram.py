import os
import re
import json
import datetime
import urllib.request
import urllib.parse
import requests
import logging

logger = logging.getLogger(__name__)

def clean_phone_number(phone):
    if not phone:
        return ""
    # Extract only digits
    digits = "".join(re.findall(r'\d', phone))
    if len(digits) == 11 and digits.startswith('8'):
        digits = '7' + digits[1:]
    return digits

def format_russian_date_and_days(event_date):
    if not event_date:
        return "—"
        
    if isinstance(event_date, str):
        try:
            event_date = datetime.datetime.strptime(event_date, "%Y-%m-%d").date()
        except ValueError:
            return event_date
            
    months_ru = {
        1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
        7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
    }
    
    formatted_date = f"{event_date.day} {months_ru[event_date.month]} {event_date.year}"
    
    today = datetime.date.today()
    delta = (event_date - today).days
    
    if delta > 0:
        return f"{formatted_date} (через {delta} дней)"
    elif delta == 0:
        return f"{formatted_date} (сегодня)"
    else:
        return f"{formatted_date} (прошло {abs(delta)} дней)"

def send_order_telegram_notification(order):
    """Sends notification about a new order."""
    name = order.name or "—"
    phone = order.phone or "—"
    contact_method = order.contact_method or "—"
    guests = order.guests or "—"
    event_date_str = format_russian_date_and_days(order.event_date)
    cart_link = order.cart_link or "—"
    
    admin_base_url = os.getenv("ADMIN_BASE_URL", "http://localhost:8000").rstrip("/")
    admin_link = f"{admin_base_url}/admin/orders/order/{order.id}/change/"
    
    total_price = f"{int(order.total_price)} ₽" if order.total_price is not None else "—"
    
    clean_phone = clean_phone_number(phone)
    social_links = []
    if clean_phone:
        social_links.append(f'<a href="https://t.me/+{clean_phone}">Telegram</a>')
        social_links.append(f'<a href="https://wa.me/{clean_phone}">WhatsApp</a>')
        social_links.append(f'<a href="https://max.ru/u/{clean_phone}">Max</a>')
    
    social_links_str = ", ".join(social_links) if social_links else "—"
    
    message = (
        f"Имя: {name}\n"
        f"Телефон: {phone}\n"
        f"Способ связи: {contact_method}\n"
        f"Количество гостей: {guests}\n"
        f"К дате: {event_date_str}\n"
        f"Корзина: {cart_link}\n"
        f"Заявка: {admin_link}\n"
        f"Итого: {total_price}\n\n"
        f"Дополнительно:\n"
        f"{social_links_str}"
    )
    
    _send_to_telegram(message)

def send_menu_request_telegram_notification(menu_request):
    """Sends notification about a new menu request."""
    name = menu_request.name or "—"
    phone = menu_request.phone or "—"
    contact_method = menu_request.contact_method or "—"
    guests = menu_request.guests or "—"
    event_date_str = format_russian_date_and_days(menu_request.date)
    
    admin_base_url = os.getenv("ADMIN_BASE_URL", "http://localhost:8000").rstrip("/")
    admin_link = f"{admin_base_url}/admin/menu_requests/menurequest/{menu_request.id}/change/"
    
    clean_phone = clean_phone_number(phone)
    social_links = []
    if clean_phone:
        social_links.append(f'<a href="https://t.me/+{clean_phone}">Telegram</a>')
        social_links.append(f'<a href="https://wa.me/{clean_phone}">WhatsApp</a>')
        social_links.append(f'<a href="https://max.ru/u/{clean_phone}">Max</a>')
    
    social_links_str = ", ".join(social_links) if social_links else "—"
    
    message = (
        f"Имя: {name}\n"
        f"Телефон: {phone}\n"
        f"Способ связи: {contact_method}\n"
        f"Количество гостей: {guests}\n"
        f"К дате: {event_date_str}\n"
        f"Корзина: —\n"
        f"Заявка: {admin_link}\n"
        f"Итого: —\n\n"
        f"Дополнительно:\n"
        f"{social_links_str}"
    )
    
    _send_to_telegram(message)

def _send_to_telegram(text):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.warning("Telegram Bot configuration (TELEGRAM_BOT_TOKEN) is missing.")
        return
        
    chat_ids = []
    
    # 1. Read directly from the Django database
    try:
        from .models import TelegramSubscriber
        active_subs = TelegramSubscriber.objects.filter(is_active=True).exclude(chat_id="")
        for sub in active_subs:
            if sub.chat_id not in chat_ids:
                chat_ids.append(sub.chat_id)
    except Exception as e:
        logger.error(f"Failed to read TelegramSubscriber list from database: {e}")
            
    # 2. Fall back to TELEGRAM_CHAT_ID from environment if no active subscribers found in DB
    env_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if env_chat_id and env_chat_id not in chat_ids:
        chat_ids.append(env_chat_id)
        
    if not chat_ids:
        logger.warning("No chat IDs found for Telegram notifications.")
        return
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    for chat_id in chat_ids:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        proxy = "http://QcFfZK:ZqwwfB@45.130.129.91:8000"
        proxies = {"http": proxy, "https": proxy}
        try:
            requests.post(url, json=payload, proxies=proxies, timeout=5)
        except Exception as e:
            logger.error(f"Failed to send Telegram notification to {chat_id}: {e}")
