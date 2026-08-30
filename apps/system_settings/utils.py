import os
import re
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def parse_proxy_string(proxy_str: str | None) -> dict | None:
    """
    Разбирает строку прокси любого формата:
      - socks5://user:pass@host:port
      - http://user:pass@host:port
      - host:port:user:pass
      - user:pass@host:port
      - host:port

    Возвращает словарь с:
      - 'scheme': 'socks5' | 'http'
      - 'host': str
      - 'port': int
      - 'user': str | None
      - 'password': str | None
      - 'requests_proxies': dict (для requests)
      - 'telethon_proxy': tuple (для Telethon TelegramClient)
      - 'url': str
    """
    if not proxy_str or not proxy_str.strip():
        return None

    s = proxy_str.strip()
    scheme = "socks5"
    user = None
    password = None
    host = ""
    port = 8000

    # 1. Формат с протоколом: socks5://... или http://...
    if "://" in s:
        parsed = urlparse(s)
        raw_scheme = parsed.scheme.lower()
        if raw_scheme.startswith("socks5") or raw_scheme.startswith("socks"):
            scheme = "socks5"
        elif raw_scheme.startswith("http"):
            scheme = "http"
        host = parsed.hostname or ""
        port = parsed.port or 8000
        user = parsed.username
        password = parsed.password
    # 2. Формат: host:port:user:pass (типичный формат от поставщиков прокси)
    elif s.count(":") == 3:
        parts = s.split(":")
        host = parts[0]
        try:
            port = int(parts[1])
        except ValueError:
            port = 8000
        user = parts[2]
        password = parts[3]
    # 3. Формат: user:pass@host:port
    elif "@" in s:
        auth_part, host_part = s.split("@", 1)
        if ":" in auth_part:
            user, password = auth_part.split(":", 1)
        else:
            user = auth_part
        if ":" in host_part:
            host, port_str = host_part.split(":", 1)
            try:
                port = int(port_str)
            except ValueError:
                port = 8000
        else:
            host = host_part
    # 4. Формат: host:port
    elif ":" in s:
        host, port_str = s.split(":", 1)
        try:
            port = int(port_str)
        except ValueError:
            port = 8000
    else:
        host = s

    if not host:
        return None

    # Для requests socks5 использует схему socks5h:// для удаленного DNS резолва
    req_scheme = "socks5h" if scheme == "socks5" else scheme
    if user and password:
        req_url = f"{req_scheme}://{user}:{password}@{host}:{port}"
    else:
        req_url = f"{req_scheme}://{host}:{port}"

    requests_proxies = {"http": req_url, "https": req_url}
    telethon_proxy = (
        (scheme, host, port, True, user, password)
        if user and password
        else (scheme, host, port)
    )

    return {
        "scheme": scheme,
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "requests_proxies": requests_proxies,
        "telethon_proxy": telethon_proxy,
        "url": req_url,
    }


def get_telegram_proxy_config() -> dict | None:
    """
    Получает конфигурацию прокси для Telegram из базы данных (SystemSettings).
    Если в базе данных прокси не задан — возвращает None (работа напрямую без прокси).
    """
    try:
        from .models import SystemSettings
        settings_obj = SystemSettings.load()
        if settings_obj and settings_obj.telegram_bot_proxy:
            parsed = parse_proxy_string(settings_obj.telegram_bot_proxy)
            if parsed:
                return parsed
    except Exception as exc:
        logger.warning("Не удалось загрузить прокси из SystemSettings: %s", exc)

    return None
