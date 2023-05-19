![Workflow status](https://github.com/Eugene-Maslov/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# Foodgram - «Продуктовый помощник»

### Описание проекта:
Фудграм - это сайт с рецептами. Здесь можно публиковать свои, добавлять понравившиеся в избранное, подписываться на авторов. Сервис «Список покупок» позволяет формировать и сохранять перечень продуктов (и их количество), которые нужны для приготовления выбранных блюд.

Проект доступен по адресу [158.160.60.184](http://158.160.60.184/recipes).
К проекту подключен [redoc](http://158.160.60.184/api/docs/redoc.html).

Данные для авторизации:

USERNAME    | EMAIL              | PASSWORD
------------|--------------------|-------------
admin       | admin@foodgram.ru  | Admin123
user1       | user1@foodgram.ru  | foodgram1
user2       | user2@foodgram.ru  | foodgram2

### Технологии:
- Python 3.7
- Django 3.2
- Django Rest Framework 3.12.4
- PostgreSQL 14.7
- Nginx 1.18.0
- Gunicorn 20.1.0
- Docker 3.8
- Docker-compose 1.29.2

### Запуск проекта:
- Клонируйте репозитрий на свой компьютер:
`$ git clone https://github.com/Eugene-Maslov/foodgram_project_react.git `
- В настройках "Actions secrets and variables" на GitHub создайте следующие secret-переменные:
    >DB_ENGINE='django.db.backends.postgresql'\
    >DB_NAME=postgres\
    >POSTGRES_USER= # Ваше имя пользователя\
    >POSTGRES_PASSWORD= # пароль для доступа к БД\
    >DB_HOST=db\
    >DB_PORT=5432\
    >SECRET_KEY= # секретный ключ из файла настроек settings.py\
    >HOST= # публичный IP-адрес, по которому планируется доступ к проекту\
    >USER= # Ваше имя пользователя для подключения к боевому серверу\
    >SSH_KEY= # приватный ключ с компьютера, имеющего доступ к боевому серверу\
    >PASSPHRASE= # фраза-пароль, использованная при создании ssh-ключа\
    >DOCKER_USERNAME= # Ваше имя пользователя на Docker Hub\
    >DOCKER_PASSWORD= # Ваш пароль от профиля на Docker Hub\
    >TELEGRAM_TO= # ID Вашего телеграм-аккаунта (можно узнать у бота @userinfobot)\
    >TELEGRAM_TOKEN= # токен Вашего бота (можно получить у бота @BotFather)\
- Чтобы настроить сервер для работы с Docker, подключитесь к нему через консоль:
`ssh <ваше_имя_пользователя>@<ваш_IP-адрес>`
- Установите на сервер Docker:
`$ sudo apt install docker.io`
- Запуште с своего компьютера изменения на GitHub, что запустит прописанные в workflow процессы по развёртыванию проекта:
`$ git add .`
`$ git commit -m "<ваш_комментарий>"`
`$ git push`
- Для доступа к функциям администратора можно на сервере создать суперюзера:
`$ sudo docker-compose exec -T web python manage.py createsuperuser`
- Или загрузить готовые данные из дампа, находящегося в папке backend:
  - загрузите дамп из папки backend локального репозитория на сервер:
  `$ scp postgres_dump.json <ваше_имя_пользователя>@<ваш_IP-адрес>:/home/<ваше_имя_пользователя>/`
  - на сервере экпортируйте данные из дампа в БД:
  `$ sudo docker-compose exec -T web python manage.py loaddata postgres_dump.json`

### После каждого обновления репозитория (push в ветку master) будет происходить:

1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
2. Сборка и доставка докер-образов frontend и backend на Docker Hub
3. Развёртывание проекта на удалённом сервере
4. Отправка сообщения в Telegram в случае успеха

### Работа с проектом: 
- Чтобы создать дамп базы:
`$ sudo docker-compose exec -T web python manage.py dumpdata > postgres_dump.json`
- Чтобы остановить все контейнеры:
`$ sudo docker-compose down`
- Чтобы остановить все контейнеры и удалить все зависимости и сети (без образов):
`$ sudo docker-compose down -v`
- Мониторинг запущенных контейнеров:
`$ sudo docker stats`
- Удалить всё, что не используется:
`$ sudo docker system prune`

## Разработчик:
_Евгений Маслов_
_Eugene.Maslov@yandex.ru_
