# Foodgram | Продуктовый помощник

**API** для платформы "**Foodgram**", где пользователи могут делиться рецептами, добавлять их в избранное и формировать список покупок.

## Описание

**Foodgram** — это платформа для публикации рецептов. Пользователи могут:

-   Регистрироваться и авторизоваться;
-   Создавать, редактировать и удалять рецепты;
-   Добавлять рецепты в избранное;
-   Формировать список покупок на основе рецептов.
-   Скачивать сводный список продуктов
-   Подписывать на любимых авторов

API позволяет управлять всеми аспектами приложения через удобные REST-запросы.

## Технологии

-   `Python 3.12`
-   `Django 5.1`
-   `Django REST Framework`
-   `Djoser`
-   `PostgreSQL`
-   `Docker` & `Docker Compose`
-   `Nginx`
-   `Gunicorn`

## Установка и запуск

1. Клонируйте репозиторий:

    ```bash
    git clone https://github.com/bissaliev/foodgram-project-react.git
    cd foodgram-project-react/
    ```

2. Cоздать и активировать виртуальное окружение:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Создайте `.env` файл с переменными окружения:

    ```bash
    SECRET_KEY=секретный ключ django
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=postgres
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    DB_HOST=db
    DB_PORT=5432

    ```

4. Перейти в директорию `backend/` и установить зависимости из файла `requirements.txt`:

    ```bash
    cd backend/
    python3 -m pip install --upgrade pip && pip install -r requirements.txt
    ```

5. Выполните миграции:

    ```bash
    python3 manage.py migrate
    ```

6. Выполните скрипт для загрузки ингредиентов:

    ```bash
    python3 manage.py load_ingredients
    ```

7. Запустите сервер-разработчика:

    ```bash
    python3 manage.py runserver
    ```

## Запуск проекта в Docker compose

-   Перейдите в директорию `infra/` и запустите `docker compose`:

    ```bash
    cd infra/
    docker compose up --build
    ```

    Проект будет доступен по адресу: [http://localhost/](http://localhost/)

-   Что остановить docker compose нажмите клавиши `Ctrl + C` и выполните команду:

    ```bash
    docker compose down -v
    ```

## Документация API

Полная документация доступна по адресу:

Swagger UI: http://127.0.0.1/api/schema/swagger-ui/

Redoc: http://127.0.0.1/api/schema/redoc/

### **Разработчик проекта**

[**Биссалиев Олег**](https://github.com/bissaliev)
