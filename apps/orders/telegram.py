import os
import re
import json
import datetime
import urllib.request
import urllib.parse
import requests
import logging
import asyncio
from telethon import TelegramClient

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
    
    def get_plural_days(n):
        n = abs(n)
        if n % 100 in [11, 12, 13, 14]:
            return "дней"
        if n % 10 == 1:
            return "день"
        if n % 10 in [2, 3, 4]:
            return "дня"
        return "дней"
    
    if delta > 0:
        return f"{formatted_date} (через {delta} {get_plural_days(delta)})"
    elif delta == 0:
        return f"{formatted_date} (сегодня)"
    else:
        abs_delta = abs(delta)
        return f"{formatted_date} (прошло {abs_delta} {get_plural_days(abs_delta)})"

def get_telegram_username_by_phone(phone):
    if not phone:
        return None
    api_id = os.getenv('TG_API_ID')
    api_hash = os.getenv('TG_API_HASH')
    if not api_id or not api_hash:
        logger.warning("TG_API_ID or TG_API_HASH not set, cannot resolve Telegram username.")
        return None
        
    session_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'anon.session')
    
    # Configure the proxy for Telethon to bypass server IP blocks and timeouts
    proxy = {
        'proxy_type': 'http',
        'addr': '45.130.129.91',
        'port': 8000,
        'username': 'QcFfZK',
        'password': 'ZqwwfB'
    }
    
    async def fetch():
        client = TelegramClient(session_path, int(api_id), api_hash, proxy=proxy)
        try:
            # Connect with a timeout to avoid blocking indefinitely
            await asyncio.wait_for(client.connect(), timeout=10.0)
            entity = await client.get_entity(phone)
            if entity and getattr(entity, 'username', None):
                return entity.username
            return None
        except Exception as e:
            logger.error(f"Error fetching Telegram entity for phone {phone}: {e}")
            return None
        finally:
            await client.disconnect()
            
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = None
        
    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return executor.submit(lambda: asyncio.run(fetch())).result()
    else:
        try:
            return asyncio.run(fetch())
        except Exception as e:
            logger.error(f"Failed running fetch in asyncio: {e}")
            return None

def get_social_links_str(phone):
    clean_phone = clean_phone_number(phone)
    if not clean_phone:
        return "—"
        
    social_links = []
    
    # 1. Telegram
    try:
        username = get_telegram_username_by_phone("+" + clean_phone)
        if username:
            social_links.append(f'<a href="https://t.me/{username}">Telegram</a>')
        else:
            social_links.append("Telegram (не найден)")
    except Exception as e:
        logger.error(f"Failed to resolve Telegram username: {e}")
        social_links.append("Telegram (ошибка поиска)")
        
    # 2. WhatsApp
    social_links.append(f'<a href="https://wa.me/{clean_phone}">WhatsApp</a>')
    
    return ", ".join(social_links)

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
    
    social_links_str = get_social_links_str(phone)
    
    # Format phone and guests with <code> tag for single-tap copy
    phone_formatted = f"<code>{phone}</code>" if phone != "—" else "—"
    guests_formatted = f"<code>{guests}</code>" if guests != "—" else "—"
    
    # Format links to be on the next line
    cart_line = f"Корзина:\n{cart_link}" if cart_link != "—" else "Корзина: —"
    admin_line = f"Заявка:\n{admin_link}"
    
    message = (
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
    
    social_links_str = get_social_links_str(phone)
    
    # Format phone and guests with <code> tag for single-tap copy
    phone_formatted = f"<code>{phone}</code>" if phone != "—" else "—"
    guests_formatted = f"<code>{guests}</code>" if guests != "—" else "—"
    
    # Format links to be on the next line (cart is always "—" here)
    cart_line = "Корзина: —"
    admin_line = f"Заявка:\n{admin_link}"
    
    message = (
        f"Имя: {name}\n"
        f"Телефон: {phone_formatted}\n"
        f"Способ связи: {contact_method}\n"
        f"Количество гостей: {guests_formatted}\n"
        f"К дате: {event_date_str}\n"
        f"{cart_line}\n"
        f"{admin_line}\n"
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
