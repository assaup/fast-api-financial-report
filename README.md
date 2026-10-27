# Finance API

REST API для учёта личных финансов: кошельки в разных валютах, доходы и расходы, переводы между кошельками с конвертацией валют, статистика расходов по категориям и приём транзакций от банка через вебхук.

Учебный проект на FastAPI.

## Возможности

- Регистрация и вход по логину и паролю, авторизация через JWT
- Кошельки в RUB, USD, EUR: создание, просмотр, переименование, удаление
- Доходы и расходы с проверкой остатка
- Переводы между кошельками с конвертацией по актуальному курсу (внешний API курсов, запасные курсы при недоступности)
- Общий баланс по всем кошелькам в рублях
- История операций с пагинацией и фильтрами (кошелёк, период, тип, категория)
- Статистика расходов по категориям за период
- Входящий вебхук банка с HMAC-подписью, защитой от повторов и идемпотентностью
- Единый формат ошибок с машинными кодами для фронтенда
- Документация OpenAPI (Swagger) с примерами ошибок

## Стек

| Назначение | Технология |
|---|---|
| Веб-фреймворк | FastAPI 0.143, Uvicorn |
| Валидация и настройки | Pydantic 2, pydantic-settings |
| База данных | PostgreSQL 17 |
| ORM | SQLAlchemy 2.1 (асинхронный режим), драйвер asyncpg |
| Миграции | Alembic |
| Аутентификация | PyJWT, bcrypt |
| HTTP-клиент | aiohttp (курсы валют) |
| Инфраструктура | Docker, Docker Compose |
| Качество кода | Ruff |

## Архитектура

Код разделён на слои, каждый отвечает за своё:

```
HTTP-запрос
   ↓
api/v1/        роутеры: принимают запрос, проверяют формат (Pydantic), вызывают сервис
   ↓
service/       бизнес-логика: правила (хватает ли денег, совпадает ли валюта), транзакции
   ↓
repository/    доступ к данным: только запросы к базе, без логики
   ↓
PostgreSQL
```

- Ошибки бизнес-логики — собственные исключения (`app/exceptions.py`), в HTTP-ответы их превращают обработчики (`app/exception_handlers.py`). Сервисы не знают про HTTP.
- Зависимости FastAPI (`app/dependency.py`): сессия базы, текущий пользователь, пагинация, проверка подписи вебхука.

## Структура проекта

```
├── app/
│   ├── api/
│   │   ├── responses.py          # описание ошибок для OpenAPI
│   │   └── v1/                   # роутеры: wallets, operations, users, stats, webhooks
│   ├── repository/               # запросы к базе
│   ├── service/                  # бизнес-логика
│   ├── config.py                 # настройки из переменных окружения
│   ├── database.py               # асинхронный движок и фабрика сессий
│   ├── dependency.py             # зависимости FastAPI
│   ├── enum.py                   # валюты и типы операций
│   ├── exceptions.py             # ошибки приложения
│   ├── exception_handlers.py     # единый формат ответов с ошибками
│   ├── models.py                 # модели SQLAlchemy
│   ├── schemas.py                # схемы Pydantic
│   └── security.py               # пароли, JWT, подпись вебхуков
├── migrations/                   # миграции Alembic
├── scripts/
│   └── send_bank_webhook.py      # имитация банка для проверки вебхука
├── tests/
├── Dockerfile
├── docker-compose.yml
├── main.py                       # создание приложения и подключение роутеров
└── pyproject.toml                # настройки Ruff
```

## Быстрый старт (Docker)

Нужен только Docker.

1. Создайте файл `.env` по образцу `.env.example` и заполните секреты:

   ```bash
   cp .env.example .env
   ```

   Сгенерировать `SECRET_KEY` и `BANK_WEBHOOK_SECRET`:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. Запустите базу и приложение:

   ```bash
   docker compose up -d --build
   ```

   При старте контейнер `app` сам применяет миграции (`alembic upgrade head`).

3. Откройте документацию: http://localhost:8000/docs

## Локальная разработка

База в Docker, приложение из виртуального окружения с автоперезагрузкой.

```bash
python -m venv venv
venv/Scripts/python.exe -m pip install -r requirements.txt   # Linux/macOS: venv/bin/python
docker compose up -d db
venv/Scripts/python.exe -m alembic upgrade head
venv/Scripts/python.exe -m uvicorn main:app --reload
```

Если запущен контейнер `app`, остановите его, чтобы освободить порт 8000: `docker compose stop app`.

## Переменные окружения

| Переменная | Обязательна | Описание |
|---|---|---|
| `SECRET_KEY` | да | ключ подписи JWT |
| `BANK_WEBHOOK_SECRET` | да | общий секрет с банком для подписи вебхуков |
| `DATABASE_URL` | да | строка подключения, например `postgresql+asyncpg://finance:пароль@localhost:5433/finance` |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | да (для Docker) | пользователь, пароль и база, которые создаёт контейнер PostgreSQL |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | нет, 30 | время жизни токена |
| `JWT_ALGORITHM` | нет, HS256 | алгоритм подписи JWT |
| `WEBHOOK_TOLERANCE_SECONDS` | нет, 300 | допустимый возраст вебхука |
| `EXCHANGE_API_URL`, `EXCHANGE_API_TIMEOUT` | нет | адрес и таймаут API курсов валют |

Порты:
- PostgreSQL снаружи Docker доступен на `localhost:5433` (5432 часто занят локальным PostgreSQL);
- внутри Docker-сети приложение подключается к `db:5432` — это значение задаётся в `docker-compose.yml`.

Файл `.env` не попадает ни в git, ни в Docker-образ.

## Миграции

```bash
venv/Scripts/python.exe -m alembic revision --autogenerate -m "описание"   # создать миграцию по изменениям моделей
venv/Scripts/python.exe -m alembic upgrade head                            # применить все миграции
venv/Scripts/python.exe -m alembic downgrade -1                            # откатить последнюю
venv/Scripts/python.exe -m alembic current                                 # текущая версия базы
venv/Scripts/python.exe -m alembic check                                   # есть ли изменения моделей без миграции
```

Сгенерированную миграцию всегда проверяйте перед применением.

## API

Все эндпоинты под префиксом `/api/v1`. Полное описание со схемами и примерами — в `/docs`.

### Аутентификация

1. `POST /api/v1/users` — регистрация (`login`, `password` от 8 символов)
2. `POST /api/v1/auth/login` — получить `access_token`
3. Передавать токен в заголовке: `Authorization: Bearer <access_token>`

### Эндпоинты

| Метод | Путь | Описание |
|---|---|---|
| POST | `/users` | регистрация |
| POST | `/auth/login` | вход, выдача JWT |
| GET | `/user/me` | текущий пользователь |
| GET | `/wallets` | список кошельков (`limit`, `offset`) |
| POST | `/wallets` | создать кошелёк |
| GET | `/wallets/{wallet_id}` | кошелёк по id |
| PATCH | `/wallets/{wallet_id}` | переименовать кошелёк |
| DELETE | `/wallets/{wallet_id}` | удалить пустой кошелёк вместе с операциями |
| GET | `/balance` | общий баланс в рублях |
| POST | `/operation/income` | доход |
| POST | `/operation/expense` | расход |
| POST | `/operation/transfer` | перевод между кошельками |
| GET | `/operations` | история (`wallet_id`, `date_from`, `date_to`, `type`, `category`, `limit`, `offset`) |
| GET | `/stats/expenses` | расходы по категориям (`wallet_id`, `date_from`, `date_to`) |
| POST | `/webhooks/bank` | вебхук банка (подпись вместо JWT) |

### Формат ошибок

Все ошибки возвращаются в одном формате:

```json
{
  "error": {
    "code": "INSUFFICIENT_FUNDS",
    "message": "Insufficient funds: available 100.00 rub, requested 500",
    "details": {"available": "100.00", "requested": "500", "currency": "rub"}
  }
}
```

- `code` — машинный код, по нему фронтенд выбирает сообщение;
- `message` — текст для разработчика и логов;
- `details` — данные для сообщения; для `VALIDATION_ERROR` — список полей `details.fields` с ошибками.

| Статус | Коды |
|---|---|
| 400 | `INSUFFICIENT_FUNDS`, `INVALID_DATE_RANGE`, `CURRENCY_MISMATCH` |
| 401 | `UNAUTHORIZED`, `INVALID_TOKEN`, `INVALID_CREDENTIALS`, `INVALID_WEBHOOK_SIGNATURE`, `WEBHOOK_EXPIRED` |
| 404 | `WALLET_NOT_FOUND`, `NOT_FOUND` |
| 405 | `METHOD_NOT_ALLOWED` |
| 409 | `WALLET_ALREADY_EXISTS`, `WALLET_NOT_EMPTY`, `USER_ALREADY_EXISTS` |
| 422 | `VALIDATION_ERROR` |
| 500 | `INTERNAL_ERROR` |

## Вебхук банка

Банк сообщает о транзакциях по счёту: приложение создаёт операцию и меняет баланс кошелька.

`POST /api/v1/webhooks/bank`

Заголовки:

| Заголовок | Значение |
|---|---|
| `X-Webhook-Timestamp` | время отправки, Unix-секунды |
| `X-Webhook-Signature` | `sha256=<HMAC-SHA256(BANK_WEBHOOK_SECRET, "<timestamp>.<тело>")>` в hex |

Тело:

```json
{
  "event_id": "evt_1a2b3c",
  "type": "transaction.created",
  "data": {
    "wallet_id": 1,
    "direction": "income",
    "amount": "150.00",
    "currency": "rub",
    "description": "Salary"
  }
}
```

Ответ: `200 {"status": "processed"}` или `200 {"status": "duplicate"}`, если событие с этим `event_id` уже обработано.

Защита:
- **подпись** — запрос отклоняется, если HMAC не совпадает (подделка или изменённое тело);
- **время** — запрос старше `WEBHOOK_TOLERANCE_SECONDS` отклоняется (повторная отправка перехваченного запроса);
- **идемпотентность** — каждый `event_id` применяется один раз, в том числе при одновременных повторах (уникальный индекс в таблице `webhook_event`).

Проверка локально — скрипт подписывает событие тем же секретом из `.env`:

```bash
venv/Scripts/python.exe -m scripts.send_bank_webhook 1 income 150.00 --description Salary
venv/Scripts/python.exe -m scripts.send_bank_webhook 1 income 150.00 --event-id evt_1   # повтор → duplicate
venv/Scripts/python.exe -m scripts.send_bank_webhook 1 income 10.00 --currency usd      # → CURRENCY_MISMATCH
```

## Качество кода

Форматирование и проверка — Ruff, настройки в `pyproject.toml`:

```bash
venv/Scripts/python.exe -m ruff format .
venv/Scripts/python.exe -m ruff check --fix .
```

## Тесты

```bash
venv/Scripts/python.exe -m pytest
```

Тесты написаны под синхронную версию проекта и требуют обновления под асинхронную базу и JWT.
