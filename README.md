CRUD API для Новостного Портала (lab1_Itodo_M_O)

Этот проект представляет собой реализацию CRUD (Create, Read, Update, Delete) API с использованием FastAPI. Сервис предназначен для управления тремя основными сущностями: Пользователи, Новости и Комментарии.
Основные технологии
Язык: Python 3.10+
Фреймворк: FastAPI
ORM: SQLAlchemy
Миграции: Alembic
СУБД: PostgreSQL
Валидация данных: Pydantic


Архитектура и проектирование
Проект имеет многоуровневую архитектуру, схожую с MVC, для четкого разделения ответственности:

app/api/routers/: Контроллеры (роутеры FastAPI), которые принимают HTTP-запросы и вызывают соответствующую бизнес-логику.
app/cure/: Сервисный слой, инкапсулирующий всю бизнес-логику приложения. Он не зависит от деталей веб-фреймворка.
app/models/: Модели данных (SQLAlchemy), описывающие структуру таблиц в базе данных.
app/schemas/: Схемы Pydantic, используемые для валидации, сериализации и десериализации данных, передаваемых через API.
app/database/: Модули для управления сессиями базы данных и базовыми конфигурациями ORM.
Core Dependencies and Configuration
requirements.txt
Database Migrations 
/alembic.ini 
Environment Configuration
app/migrations/env.py

Docker Configuration
docker-compose.yml

Схема базы данных
Модели данных и их связи спроектированы следующим образом:
Один Пользователь может быть автором множества Новостей и Комментариев.
Одна Новость может иметь множество Комментариев.
При удалении Новости все связанные с ней Комментарии также удаляются (каскадное удаление).
При удалении Пользователя все его Новости и Комментарии также удаляются.
code

Mermaid
Diagram
    USER ||--o{ NEWS : "является автором"
    USER ||--o{ COMMENT : "является автором"
    NEWS ||--o{ COMMENT : "содержит"

    USER {
        int id PK
        string name "Имя"
        string email UK "Email"
        datetime registered_at "Дата регистрации"
        boolean is_author "Верифицирован как автор"
        string avatar_url "URL аватарки"
    }
    NEWS {
        int id PK
        string title "Заголовок"
        json content "Контент (JSON)"
        datetime published_at "Дата публикации"
        int author_id FK "ID автора"
        string cover_image_url "URL обложки"
    }
    COMMENT {
        int id PK
        string text "Текст"
        int news_id FK "ID новости"
        int author_id FK "ID автора"
        datetime published_at "Дата публикации"
    }

Установка и запуск
Предварительные требования
Python 3.10 или новее
Git
Установленная и запущенная СУБД PostgreSQL
Пошаговая инструкция
1. Клонируйте репозиторий:

git clone <URL_ВАШЕГО_ПРИВАТНОГО_РЕПОЗИТОРИЯ>
https://github.com/itmo-webdev/Lab1_Itodo_M_O.git
cd lab1_Itodo_M_O

2. Создайте и активируйте виртуальное окружение:

Run with Docker (Recommended)

# Для Unix/macOS
python3 -m venv venv
source venv/bin/activate
 docker-compose up --build
# Для Windows
python -m venv venv
venv\Scripts\activate

3. Установите зависимости:
pip install -r requirements.txt

4. Настройте подключение к базе данных:
Скопируйте файл .env.example в .env и укажите в нем свои данные для подключения к PostgreSQL.
  DATABASE_URL=postgresql://user:password@localhost:5432/news_db
5. Примените миграции базы данных:
Эта команда создаст все необходимые таблицы и заполнит их начальными (моковыми) данными.```bash
alembic upgrade head

**6. Запустите приложение:**
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

Сервер будет доступен по адресу http://127.0.0.1:8000.
Интерактивная документация API (Swagger UI) доступна по адресу:
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redocs
Примеры использования API (через curl)
 Пользователи
Создание пользователя
curl -X 'POST' \
  'http://127.0.0.1:8000/users/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Сергей Петров",
  "email": "sergey.p@example.com",
  "is_author": true,
  "avatar_url": "https://example.com/images/sergey.png"
}'


Получение списка всех пользователей

curl -X 'GET' 'http://127.0.0.1:8000/users/' -H 'accept: application/json'


Новости
ВАЖНО: Создавать новости могут только пользователи с флагом is_author: true. ID автора (author_id) должен существовать в базе данных.

curl -X 'POST' \
  'http://127.0.0.1:8000/news/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "FastAPI: Новые горизонты",
  "content": {
    "type": "article",
    "body": "FastAPI продолжает набирать популярность...",
    "tags": ["python", "api", "fastapi"]
  },
  "author_id": 1,
  "cover_image_url": "https://example.com/images/fastapi-cover.png"
}'

Получение новости по ID

curl -X 'GET' 'http://127.0.0.1:8000/news/1' -H 'accept: application/json'


Изменение новости
curl -X 'PUT' \
  'http://127.0.0.1:8000/news/1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "FastAPI: Обновленные горизонты 2025",
  "content": {
    "type": "article",
    "body": "В этой обновленной статье мы рассмотрим новые возможности фреймворка.",
    "tags": ["python", "api", "fastapi", "2025"]
  }
}'

Удаление новости
При выполнении этого запроса также будут удалены все комментарии, связанные с этой новостью.

curl -X 'DELETE' 'http://127.0.0.1:8000/news/1' -H 'accept: application/json'


 Комментарии
Создание комментария к новости
ID автора (author_id) и новости (news_id) должны существовать.

curl -X 'POST' \
  'http://127.0.0.1:8000/comments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "Отличная статья! Очень информативно.",
  "news_id": 2,
  "author_id": 1
}'


Получение всех комментариев к новости

curl -X 'GET' 'http://127.0.0.1:8000/news/2/comments' -H 'accept: application/json'



Удаление комментария
curl -X 'DELETE' 'http://127.0.0.1:8000/comments/1' -H 'accept: application/json'

Работа с миграциями (Alembic)
Alembic используется для управления версиями схемы базы данных.


#Создать новую авто-генерируемую миграцию (после изменения моделей SQLAlchemy):
alembic revision --autogenerate -m "Краткое описание изменений"


 #Применить последнюю миграцию:
alembic upgrade head

 #Откатить последнюю миграцию:
alembic downgrade -1
 
 #Show migration history
alembic history




# Клонирование и запуск за 5 минут
git clone https://github.com/itmo-webdev/lab1_Itodo_M_O.git
cd lab1_Itodo_M_O
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Настройка БД (требуются права sudo)
sudo service postgresql start
sudo -u postgres psql -c "CREATE USER news_user WITH PASSWORD 'news_password';"
sudo -u postgres psql -c "CREATE DATABASE news_db OWNER news_user;"

echo "DATABASE_URL=postgresql://news_user:news_password@localhost:5432/news_db" > .env
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
