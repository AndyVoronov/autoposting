# Autoposting Platform

Веб-платформа для управления множеством каналов в социальных сетях с автоматической генерацией и публикацией контента.

## Быстрый старт

```bash
# Клонирование
git clone <repo-url>
cd autoposting

# Настройка окружения
cp .env.example .env
# Отредактируйте .env с вашими настройками

# Запуск
docker-compose up -d

# Логи
docker-compose logs -f
```

## Доступ

- Frontend: http://localhost
- API: http://localhost/api
- Документация API: http://localhost/api/docs

## Дефолтный логин

- Username: `admin`
- Password: `admin123`

## Структура проекта

```
autoposting/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # REST endpoints
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── services/  # Business logic
│   │   └── utils/     # Utilities
│   └── tests/
├── frontend/          # Vue 3 frontend
│   └── src/
│       ├── views/     # Page components
│       ├── stores/    # Pinia stores
│       ├── api/       # API client
│       └── router/    # Vue Router
├── nginx/             # Nginx config
└── docker-compose.yml
```

## Технологии

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery
- **Frontend**: Vue 3, Vite, TailwindCSS, Pinia
- **Deploy**: Docker, Nginx

## Разработка

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Лицензия

MIT
