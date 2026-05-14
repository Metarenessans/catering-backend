# Catering Backend API (Django REST Framework)

Это полноценный REST API backend для проекта «Шеф Мил Фуршет». Он предоставляет функционал каталога продуктов, оформления заказов через корзину, обработки заявок на подбор меню, управления FAQ и информацией о компании.

## 📌 Архитектура и стек технологий
- **Backend Framework:** Django 5.0
- **API Framework:** Django REST Framework (DRF)
- **База данных:** PostgreSQL
- **Аутентификация:** JWT (SimpleJWT)
- **Документация:** Swagger / OpenAPI 3 (drf-spectacular)
- **CORS:** Настроен для работы с frontend-приложением на `localhost:3000`
- **Структура приложений (Django Apps):**
  - `catalog` — категории, продукты (блюда), фильтрация.
  - `orders` — заказы из корзины (с сохранением снимков цен/названий).
  - `menu_requests` — заявки на подбор меню (с форматами и доп. услугами).
  - `faq` — управление часто задаваемыми вопросами.
  - `company` — singleton модель с настройками компании (минимальная сумма заказа, контакты).

## 🚀 Инструкция по запуску

### 1. Настройка окружения
Перейдите в папку `backend/` и создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # На Linux/Mac
venv\Scripts\activate     # На Windows
```

Установите зависимости:
```bash
pip install -r requirements.txt
```

### 2. Конфигурация (.env)
Скопируйте пример файла конфигурации:
```bash
cp .env.example .env
```
Убедитесь, что в `.env` указаны правильные доступы к вашей локальной базе данных PostgreSQL.

### 3. Запуск PostgreSQL
Убедитесь, что у вас запущен PostgreSQL и создана база данных (по умолчанию `catering_db`):
```sql
CREATE DATABASE catering_db;
CREATE USER postgres WITH PASSWORD 'postgres';
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE catering_db TO postgres;
```

### 4. Миграции и подготовка базы данных
Выполните миграции:
```bash
python manage.py makemigrations catalog orders menu_requests faq company
python manage.py migrate
```

Создайте суперпользователя для доступа к админ-панели:
```bash
python manage.py createsuperuser
```

### 5. Загрузка демонстрационных данных (Mock Data)
Мы подготовили management command, которая загружает категории, товары, FAQ и форматы мероприятий на основе mock-данных из frontend:
```bash
python manage.py load_mock_data
```

### 6. Запуск сервера
Запустите development-сервер:
```bash
python manage.py runserver
```

## 📚 Документация API и Панель управления
После запуска сервера вам будут доступны:
- **Админ-панель Django:** http://127.0.0.1:8000/admin/
- **Swagger UI (Документация API):** http://127.0.0.1:8000/api/docs/
- **ReDoc:** http://127.0.0.1:8000/api/redoc/

В админ-панели настроена полная поддержка фильтрации, поиска, сортировки и редактирования связанных сущностей (через `inlines`).
