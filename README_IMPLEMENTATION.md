# Реализация тестового задания

## Описание реализованного функционала

### 1. Модель данных

#### Channel (Канал)
- `name` - название канала
- `chat_bot_id` - ID чат-бота, к которому подключен канал
- `settings` - настройки канала (webhook_url и token)
- `is_active` - статус активности канала

#### ChatBot (Чат-бот)
- `name` - название чат-бота
- `secret_token` - секретный токен для аутентификации

#### Dialogue (Диалог)
- `chat_bot_id` - ID чат-бота
- `message_list` - список сообщений в диалоге

### 2. API эндпоинты

#### Управление каналами (`/api/channels/`)

- `POST /api/channels/` - создание нового канала
- `GET /api/channels/` - получение списка каналов (с фильтрацией по chat_bot_id)
- `GET /api/channels/{channel_id}` - получение канала по ID
- `PUT /api/channels/{channel_id}` - обновление канала
- `DELETE /api/channels/{channel_id}` - удаление канала
- `GET /api/channels/{channel_id}/dialogue` - получение истории диалога для канала

#### Webhook (`/api/webhook/`)

- `POST /api/webhook/new_message` - получение сообщений из канала

### 3. Бизнес-логика

#### ChatService
- Обработка входящих сообщений
- Проверка дублирования сообщений
- Игнорирование сообщений от сотрудников
- Генерация ответов через LLM
- Отправка ответов в каналы

#### ChannelService
- CRUD операции с каналами
- Валидация существования чат-ботов
- Управление настройками каналов

### 4. Безопасность

- Аутентификация через Bearer токены
- Валидация токенов чат-ботов
- Проверка прав доступа к каналам

### 5. Особенности реализации

- Чат-бот не отвечает дважды на одно и то же сообщение
- Чат-бот не отвечает на сообщения сотрудников
- Сохранение контекста диалогов
- Асинхронная обработка сообщений
- Отправка сообщений во все активные каналы чат-бота

## Запуск приложения

### Требования
- Python 3.13+
- MongoDB
- Poetry или pip

### Установка зависимостей
```bash
pip install -e .
```

### Настройка окружения
Создайте файл `.env`:
```
MONGO__URL=mongodb://localhost:27017
MONGO__DB_NAME=chatbot
```

### Запуск
```bash
python -m src.main
```

Приложение будет доступно по адресу `http://localhost:80`

## Тестирование

### Установка тестовых зависимостей
```bash
pip install pytest pytest-asyncio httpx motor
```

### Запуск тестов
```bash
# Убедитесь, что MongoDB запущен
MONGO__URL=mongodb://localhost:27017 MONGO__DB_NAME=chatbot_test python -m pytest tests/ -v
```

## Структура проекта

```
src/
├── app/
│   ├── routers/
│   │   └── api/
│   │       ├── channels.py      # API для управления каналами
│   │       ├── webhook.py       # Webhook для получения сообщений
│   │       └── hello_world.py   # Тестовый эндпоинт
│   ├── schemas/                 # Pydantic модели для API
│   ├── services/                # Бизнес-логика
│   └── app.py                   # Основное приложение FastAPI
├── core/
│   ├── database/
│   │   ├── models/              # Модели данных
│   │   └── registry.py          # Инициализация базы данных
│   ├── settings_model.py        # Настройки приложения
│   └── logs/                    # Конфигурация логирования
├── predict/
│   └── mock_llm_call.py        # Мок для LLM
└── main.py                      # Точка входа
```

## Примеры использования

### Создание канала
```bash
curl -X POST "http://localhost/api/channels/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Telegram Channel",
    "chat_bot_id": "chatbot_id_here",
    "webhook_url": "https://api.telegram.org/bot123/webhook",
    "token": "channel_token_here"
  }'
```

### Отправка сообщения в webhook
```bash
curl -X POST "http://localhost/api/webhook/new_message" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer chatbot_token_here" \
  -d '{
    "message_id": "msg_123",
    "chat_id": "chat_456",
    "text": "Hello, bot!",
    "message_sender": "customer"
  }'
```

## Дополнительные возможности

- Автоматическое создание диалогов при первом сообщении
- Логирование ошибок при отправке сообщений в каналы
- Валидация входных данных через Pydantic
- Асинхронная обработка для высокой производительности
- Поддержка множественных каналов для одного чат-бота
