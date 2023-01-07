# Проект Продуктовый помощник

[Foodgram workflow](https://github.com/bissaliev/foodgram-project-react/actions/workflows/main.yml/badge.svg)


## **Описание**
Проект Foodgram, «Продуктовый помощник». На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## **Техническая информация:**
Стек технологий: Python 3, Django, Django Rest Framework, React, Docker, PostgreSQL, nginx, gunicorn, Djoser.

- Веб-сервер: nginx (контейнер nginx)
- Frontend фреймворк: React (контейнер frontend)
- Backend фреймворк: Django (контейнер backend)
- API фреймворк: Django REST (контейнер backend)
- База данных: PostgreSQL (контейнер db)

## **Установка проекта локально:**
- Склонировать репозиторий на локальную машину:

  `git clone https://github.com/bissaliev/foodgram-project-react.git`
  
  `cd foodgram-project-react`

- Cоздать и активировать виртуальное окружение:

  `python -m venv venv`
  
  `source venv/Scripts/activate`
  
- Cоздайте файл .env в директории /infra/ с содержанием:

  `SECRET_KEY=секретный ключ django`
  `DB_ENGINE=django.db.backends.postgresql`
  `DB_NAME=postgres`
  `POSTGRES_USER=postgres`
  `POSTGRES_PASSWORD=postgres`
  `DB_HOST=db`
  `DB_PORT=5432`

- Перейти в директирию, обновить pip и установить зависимости из файла requirements.txt:

  `cd backend/`
  
  `python -m pip install --upgrade pip &&`
  `pip install -r backend/requirements.txt`
- Выполните миграции:

  `python manage.py migrate`

- Запустите сервер:

  `python manage.py runserver`

## **Запуск проекта в Docker контейнере:**
- Из папки "./infra/" выполнить команду:

  `docker-compose up -d`

- После успешного запуска контейнеров выполнить миграции:

  `docker-compose exec backend python manage.py migrate`
- Создать суперюзера (Администратора):

  `docker-compose exec backend python manage.py createsuperuser`
- Проект можно проверить по адресу: [http://localhost/](http://localhost/)
- Заполнение базы данных ингредиентами

  `docker-compose exec backend python manage.py load_ingridients`
## **Разработчик проекта:**
***Биссалиев Олег Кайдырович***

