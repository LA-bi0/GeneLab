# GeneLab

## Платформа для анализа биологических данных

GeneLab — учебный full-stack проект по биоинформатике, разработанный как университетское портфолио. Система предоставляет базовый API для регистрации пользователей, создания исследовательских проектов, загрузки DNA-последовательностей и автоматического анализа FASTA-файлов.

Текущий backend реализует полный минимальный сценарий обработки данных:

```text
Пользователь -> Проект -> FASTA-файл -> фоновый анализ -> метрики в SQLite
```

На следующем этапе к API будет подключен React-интерфейс для работы с этими возможностями через браузер.

## Возможности текущей версии

- регистрация пользователя с валидацией входных данных;
- безопасное хэширование паролей с помощью PBKDF2-HMAC-SHA256;
- вход пользователя с базовым development-токеном;
- создание исследовательских проектов;
- загрузка `.fasta`-файлов через `multipart/form-data`;
- сохранение исходных файлов в `storage/raw`;
- чтение FASTA через Biopython;
- расчет общей длины DNA-последовательностей;
- точный расчет GC-состава в процентах;
- обработка файла в FastAPI `BackgroundTasks`, чтобы не выполнять анализ внутри основного HTTP-обработчика;
- статусы обработки датасета: `processing`, `completed`, `error`;
- сохранение результатов анализа, SHA-256 checksum и метаданных в SQLite.

## Технологический стек

### Backend

| Технология | Назначение |
|---|---|
| Python 3.13+ | основной язык backend и научных вычислений |
| FastAPI | REST API, валидация запросов и OpenAPI-документация |
| Uvicorn | ASGI-сервер для запуска приложения |
| Pydantic | схемы запросов и ответов |
| SQLAlchemy 2.x | ORM и работа с базой данных |
| SQLite | локальная реляционная база данных на этапе разработки |
| Biopython | разбор и обработка биологических последовательностей |
| NumPy, Pandas | последующие численные и табличные анализы |
| scikit-learn | последующее добавление моделей машинного обучения |

### Хранение данных

- база данных: `genelab.db` в корне проекта;
- исходные загруженные файлы: `storage/raw`;
- уникальные имена файлов генерируются через UUID;
- для каждого файла вычисляется SHA-256 checksum;
- структура доступа к БД инкапсулирована в `backend/app/core/database.py`.

## Структура проекта

```text
GeneLab/
├── backend/
│   ├── app/
│   │   ├── main.py                 # точка входа FastAPI
│   │   ├── core/
│   │   │   └── database.py         # SQLite, engine, Base и DB-сессии
│   │   ├── models/
│   │   │   ├── user.py              # SQLAlchemy-модель User
│   │   │   ├── project.py           # SQLAlchemy-модель Project
│   │   │   └── dataset.py           # SQLAlchemy-модель Dataset
│   │   ├── schemas/
│   │   │   ├── auth.py              # Pydantic-схемы авторизации
│   │   │   ├── project.py           # схемы проекта
│   │   │   └── dataset.py           # схема ответа датасета
│   │   ├── api/
│   │   │   ├── auth.py              # auth endpoints
│   │   │   └── projects.py          # проекты и загрузка файлов
│   │   ├── services/
│   │   │   └── dna_service.py       # FASTA-парсер и DNA-метрики
│   │   └── workers/
│   │       └── tasks.py             # фоновые задачи анализа
│   └── migrations/                  # место для будущих Alembic-миграций
├── frontend/                        # React-приложение, Этап 8
├── storage/
│   ├── raw/                         # исходные FASTA-файлы
│   ├── processed/                   # обработанные данные
│   └── results/                     # будущие файлы результатов
├── docs/                            # техническая документация
├── tests/                           # общие тесты проекта
├── genelab.db                       # локальная SQLite-база создается при запуске
├── requirements.txt                 # Python-зависимости
└── README.md
```

> В имени базы данных используется `genelab.db`. В файловой структуре выше это имя следует читать именно в ASCII-виде: `genelab.db`.

## Модель данных

### User

Таблица `users` содержит учетные записи пользователей:

- `id` — UUID пользователя;
- `email` — уникальный email;
- `password_hash` — PBKDF2-хэш, исходный пароль не сохраняется;
- `full_name` — отображаемое имя;
- `role` — текущая роль, по умолчанию `user`;
- `created_at` — время регистрации.

### Project

Таблица `projects` описывает исследовательские проекты:

- `id` — UUID проекта;
- `owner_id` — внешний ключ на `users.id`;
- `name` — название проекта;
- `description` — описание;
- `organism` — исследуемый организм;
- `visibility` — видимость проекта, по умолчанию `private`;
- `created_at`, `updated_at` — временные метки.

### Dataset

Таблица `datasets` связана с проектом через `project_id` и хранит:

- имя и исходное имя файла;
- относительный путь к сохраненному FASTA;
- формат, размер файла и SHA-256 checksum;
- `sequence_length` — суммарное количество нуклеотидов;
- `gc_content` — процент G и C среди всех нуклеотидов;
- `status` — `processing`, `completed` или `error`;
- `error_message` — описание ошибки, если анализ не завершился;
- `created_at`.

GC-состав вычисляется по формуле:

```text
GC% = (количество G + количество C) / общее количество нуклеотидов * 100
```

Поддерживаются DNA-символы `A`, `C`, `G`, `T` и `N`. При обнаружении других символов задача переводит датасет в состояние `error`.

## API

Все endpoints доступны без дополнительного префикса `/api/v1` в текущей версии. Автоматическая документация FastAPI доступна по адресам `/docs` и `/redoc`.

### Проверка сервера

#### `GET /`

Возвращает состояние приложения:

```json
{
	"status": "ok",
	"project": "GeneLab"
}
```

### Регистрация

#### `POST /auth/register`

Создает пользователя и возвращает профиль с development-токеном.

Тело запроса:

```json
{
	"email": "student@example.com",
	"password": "StrongPass123",
	"full_name": "Student User"
}
```

Ограничения:

- пароль: от 8 до 128 символов;
- email нормализуется к нижнему регистру;
- email должен быть уникальным;
- повторная регистрация возвращает `409 Conflict`.

Успешный ответ: `201 Created`.

### Вход

#### `POST /auth/login`

Проверяет email и пароль, после чего возвращает пользователя и базовый токен:

```json
{
	"email": "student@example.com",
	"password": "StrongPass123"
}
```

Успешный ответ содержит:

```json
{
	"user": {
		"id": "user-uuid",
		"email": "student@example.com",
		"full_name": "Student User",
		"role": "user",
		"created_at": "2026-08-25T12:00:00"
	},
	"access_token": "dev-token-user-uuid",
	"token_type": "bearer"
}
```

Неверные учетные данные возвращают `401 Unauthorized`.

> `dev-token-*` предназначен только для текущего учебного этапа. Перед публикацией production-версии он должен быть заменен на JWT или другой полноценный механизм сессий.

### Создание проекта

#### `POST /projects`

Создает проект для существующего пользователя.

Тело запроса:

```json
{
	"owner_id": "user-uuid",
	"name": "E. coli DNA study",
	"description": "Исследование состава DNA",
	"organism": "Escherichia coli",
	"visibility": "private"
}
```

Успешный ответ: `201 Created`. Если владелец не найден, API возвращает `404 Not Found`.

### Загрузка и анализ FASTA

#### `POST /projects/{project_id}/datasets`

Принимает файл в формате `multipart/form-data`:

```text
file: sample.fasta
```

Алгоритм endpoint:

1. Проверяет существование проекта.
2. Проверяет расширение `.fasta`.
3. Сохраняет файл в `storage/raw` под UUID-именем.
4. Создает запись `Dataset` со статусом `processing`.
5. Добавляет `process_dataset` в FastAPI `BackgroundTasks`.
6. Возвращает метаданные датасета клиенту.

Фоновая задача:

1. Открывает собственную SQLAlchemy-сессию.
2. Передает файл в `dna_service.analyze_fasta`.
3. Читает все FASTA-записи через `Bio.SeqIO`.
4. Суммирует длины последовательностей и количество `G`/`C`.
5. Сохраняет `sequence_length` и `gc_content`.
6. Переводит запись в `completed` либо `error`.

На момент ответа endpoint статус обычно равен `processing`; после выполнения фоновой задачи он становится `completed` или `error`.

Пример ответа:

```json
{
	"id": "dataset-uuid",
	"project_id": "project-uuid",
	"name": "sample",
	"file_name": "sample.fasta",
	"file_format": "fasta",
	"file_size": 42,
	"checksum": "sha256-hex-value",
	"sequence_length": null,
	"gc_content": null,
	"status": "processing",
	"error_message": null,
	"created_at": "2026-08-25T12:00:00"
}
```

## Запуск backend

Из корневой папки проекта:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload
```

Сервер будет доступен по адресу `http://127.0.0.1:8000`.

Документация API:

- Swagger UI: `http://127.0.0.1:8000/docs`;
- ReDoc: `http://127.0.0.1:8000/redoc`.

Также сервер можно запустить напрямую:

```powershell
python backend/app/main.py
```

## Пример проверки через PowerShell

Регистрация пользователя:

```powershell
$body = '{"email":"student@example.com","password":"StrongPass123","full_name":"Student User"}'
Invoke-RestMethod -Uri http://127.0.0.1:8000/auth/register -Method Post -ContentType 'application/json' -Body $body
```

Создание проекта выполняется с использованием значения `id` зарегистрированного пользователя:

```powershell
$projectBody = '{"owner_id":"USER_ID","name":"DNA study","organism":"E. coli"}'
Invoke-RestMethod -Uri http://127.0.0.1:8000/projects -Method Post -ContentType 'application/json' -Body $projectBody
```

Загрузка FASTA-файла:

```powershell
curl.exe -X POST `
	-F "file=@sample.fasta" `
	http://127.0.0.1:8000/projects/PROJECT_ID/datasets
```

## Архитектурные решения

### Разделение ответственности

- `api` отвечает за HTTP-контракт и коды ошибок;
- `schemas` валидирует входные и выходные данные;
- `models` описывает структуру SQLite;
- `services` содержит предметную логику биоинформатического анализа;
- `workers` запускает длительные операции отдельно от основного обработчика запроса;
- `core` содержит общую инфраструктуру приложения.

### Почему SQLite

SQLite бесплатна, не требует отдельного сервера и хорошо подходит для локальной учебной разработки и демонстрации проекта. Слой SQLAlchemy изолирует приложение от конкретной СУБД, поэтому в дальнейшем SQLite можно заменить на PostgreSQL с минимальными изменениями.

### Ограничения текущей версии

- `BackgroundTasks` подходит для базового MVP, но не заменяет распределенную очередь;
- для production-анализа больших файлов потребуется Celery или RQ с Redis;
- development-токен еще не обеспечивает полноценную авторизацию;
- миграции Alembic и автоматические тесты будут расширяться по мере развития проекта;
- frontend пока находится на этапе подготовки.

## План Этапа 8: React frontend

Следующий этап посвящен подключению React-интерфейса к готовому backend API:

1. настроить React + TypeScript + Vite;
2. добавить маршрутизацию и базовый layout;
3. создать страницы регистрации и входа;
4. добавить список проектов и форму создания проекта;
5. реализовать загрузку FASTA через `FormData`;
6. отображать статус фоновой обработки и результаты GC-анализа;
7. добавить интерактивное представление биоинформатических метрик.

README будет обновляться вместе с появлением новых пользовательских сценариев и API-контрактов.
