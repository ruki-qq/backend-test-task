# Платформа для управления чат-ботами

Приложение для подключения каналов (мессенджеры/CRM/и т.п.) к чат-ботам, получения входящих сообщений через вебхук, хранения контекста диалогов и отправки ответов в каналы.

Фокус: демонстрация интеграции каналов, маршрутизации сообщений, хранения диалогов и базовой имитации LLM-ответа.


## Содержание
- Особенности и возможности
- Архитектура и стек
- Установка и запуск
- Конфигурация окружения
- API
  - Управление каналами
  - Webhook приёма сообщений
  - Формат исходящих сообщений в каналы
- Модели данных
- Логика обработки сообщений
- Тестирование
- Структура проекта


## Особенности и возможности
- Подключение нескольких каналов к одному чат‑боту
- Приём входящих сообщений из канала через вебхук
- Сохранение контекста диалогов по (chat_bot_id + chat_id)
- Игнорирование сообщений от сотрудников
- Защита от повторной обработки одного и того же сообщения (по text и/или message_id)
- Отправка ответов чат‑бота во все активные каналы, подключённые к боту
- Мок-LLM (mock_llm_call) имитирует ответ ассистента


## Архитектура и стек
- FastAPI — REST API
- Beanie (MongoDB ODM) + Motor — работа с MongoDB
- Pydantic/Pydantic Settings — схемы и конфигурация
- Loguru — логирование
- Uvicorn — сервер


## Установка и запуск
Требования: Python 3.13+, запущенный MongoDB

1) Клонирование и установка зависимостей

```
python -m venv .venv
source .venv/bin/activate
poetry install --sync.
```

2) Настройка окружения (.env)

Создайте файл .env (значения по умолчанию приведены ниже в разделе «Конфигурация окружения»).

3) Запуск приложения

```
python -m src.main
```

По умолчанию приложение поднимется на 0.0.0.0:8000. 
Документация доступна по адресу http://localhost:8000/docs


## Конфигурация окружения
Конфигурация читается из .env (и/или переменных окружения) через pydantic-settings.

Поддерживаемые переменные:
- MONGO__URL — строка подключения к MongoDB (по умолчанию mongodb://localhost:27017)
- MONGO__DB_NAME — имя базы (по умолчанию chatbot_test)
- SERVER__WORKERS — количество воркеров uvicorn (по умолчанию 1)

Пример .env:
```
MONGO__URL=mongodb://localhost:27017
MONGO__DB_NAME=chatbot
SERVER__WORKERS=1
```


## API
Базовый префикс — /api

### 1) Управление каналами — /api/channels/

- POST /api/channels/
  - Создать канал и привязать его к чат-боту
  - Request JSON:
    {
      "name": "str",
      "chat_bot_id": "<ObjectId строкой>",
      "url": "https://example.com/webhook",
      "is_active": true  // необязательно, по умолчанию true
    }
  - Response JSON:
    {
      "id": "<id канала>",
      "name": "...",
      "chat_bot_id": "<id бота>",
      "url": "https://...",
      "is_active": true,
      "token": "<автосгенерированный токен канала>"
    }

- GET /api/channels/
  - Получить список каналов
  - Параметры: chat_bot_id (опционально), active=true|false (опционально)

- GET /api/channels/{channel_id}
  - Получить канал по id

- PUT /api/channels/{channel_id}
  - Обновить поля: name, url, is_active

- DELETE /api/channels/{channel_id}
  - Удалить канал

- GET /api/channels/{channel_id}/dialogue
  - Получить историю диалога для канала (сериализованный список сообщений)


### 2) Webhook приёма сообщений — POST /api/webhook/new_message

- Заголовок авторизации (токен чат‑бота):
  - chat_bot_authorization: Bearer <секретный_токен_бота>
- Тело запроса (JSON):
  {
    "message_id": "str | null",  // необязательно
    "chat_id": "str",            // идентификатор чата в канале
    "text": "str",
    "message_sender": "customer" | "employee"
  }
- Ответ: { "status": "Message processed successfully" }

Поведение:
- Если message_sender == "employee" — сообщение игнорируется
- Если сообщение уже обрабатывалось (совпадение по text и/или message_id) — повторная обработка игнорируется
- Для новых сообщений:
  - Сообщение добавляется в контекст диалога (роль USER)
  - Генерируется ответ ассистента (mock_llm_call)
  - Ответ добавляется в контекст диалога (роль ASSISTANT)
  - Ответ отправляется в подключённые активные каналы бота


### 3) Формат исходящих сообщений в каналы
Для каждого активного канала, подключённого к боту, выполняется POST на URL: channel.settings.url

- Заголовки:
  - chat_authorization: Bearer <token_канала>
  - Content-Type: application/json
- Тело:
  {
    "event_type": "new_message",
    "chat_id": "str",
    "text": "str"
  }

Примечание: токен канала выдаётся при создании канала и хранится в channel.settings.token


## Модели данных (MongoDB)

- ChatBot
  - name: str
  - secret_token: str

- Channel
  - name: str
  - chat_bot_id: ObjectId
  - settings: { url: HttpUrl, token: str }
  - is_active: bool = true

- Dialogue
  - chat_bot_id: ObjectId
  - chat_id: str
  - message_list: DialogueMessage[]

- DialogueMessage
  - role: "ASSISTANT" | "SYSTEM" | "USER"
  - text: str
  - message_id: str | null


## Логика обработки сообщений
1) Вебхук получает входящее сообщение
2) Проверяется токен бота по заголовку chat_bot_authorization
3) Сообщения от сотрудников (employee) игнорируются
4) Проверка на дубликаты: по тексту и (если задан) по message_id
5) Сообщение пользователя добавляется в историю диалога
6) Вызывается mock_llm_call для генерации ответа ассистента
7) Ответ ассистента сохраняется в диалог
8) Ответ отправляется в подключённые активные каналы данного бота


## Тестирование
1) Убедитесь, что MongoDB запущен
2) Запуск тестов (используется отдельная БД из настроек):

```
MONGO__URL=mongodb://localhost:27017 MONGO__DB_NAME=chatbot_test python -m pytest -v
```

Покрытие тестами:
- CRUD каналов
- Фильтрации каналов
- Webhook: успешная обработка, игнорирование сообщений от сотрудников, проверка токена/заголовков, защита от дублей
- Наличие основных роутов


## Структура проекта
```
src/
├─ app/
│  ├─ app.py                    # Инициализация FastAPI
│  ├─ routers/
│  │  └─ api/
│  │     ├─ channels.py         # API каналов
│  │     └─ webhook.py          # Webhook приёма сообщений
│  ├─ schemas/                  # Pydantic-схемы
│  └─ services/
│     ├─ channel_service.py     # Логика каналов
│     └─ chat_service.py        # Логика чатов/диалогов/рассылок
├─ core/
│  ├─ database/
│  │  ├─ models/                # Модели Beanie
│  │  └─ registry.py            # Инициализация Mongo
│  └─ settings_model.py         # Настройки приложения
├─ predict/
│  └─ mock_llm_call.py          # Мок LLM вызова
└─ main.py                      # Точка входа
```


---

Примечание: Если интеграционная среда требует иного имени заголовка авторизации, его легко заменить в ChatService (как для входящих, так и для исходящих запросов).
