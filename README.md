# Проект yamdb_final
### Ссылка на развернутый проект
```
http://51.250.28.133/admin/
```
### Описание
Проект api_yamdb собирает отзывы (Review) пользователей на произведения (Titles). Произведения делятся на категории (Category) каждому произведению может быть присвоен жанр (Genre). 
Сами произведения в проекте не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
Процедура запуска проекта представлена ниже.
### Технологии
asgiref 3.2.10
Django 2.2.16
django-filter 2.4.0
djangorestframework 3.12.4
djangorestframework-simplejwt 4.8.0
gunicorn 20.0.4
psycopg2-binary 2.8.6
PyJWT 2.1.0
pytz 2020.1
sqlparse 0.3.1
Docker 23.0.1
Docker-compose 1.29.2
### Шаблон наполнения env-файла
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД 
```
### Запуск проекта, развертка контейнеров
- Заполните env-файл
- Перейдите в директорию yamdb_final/infra/
- Выполните команду 
```
docker-compose up -d
```
- Далее примените миграции, создайте суперпользователя и "соберите статику",
по очереди выполнив следующие команды:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```
### Авторы
iArt0s
### Workflow status
![yamdb workflow](https://github.com/iArt0s/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)