# Автопостинг — Техническое задание

## Описание проекта

Веб-платформа для управления множеством каналов в социальных сетях (Telegram, VK, WordPress) с автоматической генерацией и публикацией контента.

---

## Технологический стек

| Компонент | Технология |
|-----------|------------|
| Backend | Python 3.11+ (FastAPI) |
| Database | PostgreSQL 15+ |
| Cache/Queue | Redis + Celery |
| Frontend | Vue 3 + Vite + TailwindCSS |
| AI | GLM-5 (z.ai API) |
| Deploy | Docker + Nginx на VPS reg.ru |
| Auth | JWT (только admin) |

---

## Архитектура системы

```
┌─────────────────────────────────────────────────────────┐
│                    Dashboard (Vue 3)                     │
├─────────────────────────────────────────────────────────┤
│  Каналы │ Очередь │ Модерация │ Аналитика │ Настройки   │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
├──────────────┬──────────────┬──────────────┬────────────┤
│ REST API     │ Celery       │ Content      │ Censorship │
│              │ Scheduler    │ Engine       │ Module     │
└──────────────┴──────────────┴──────────────┴────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                   Publishers                             │
├──────────────┬──────────────┬──────────────┬────────────┤
│ Telegram API │ VK API       │ WordPress    │            │
└──────────────┴──────────────┴──────────────┴────────────┘
```

---

## Типы каналов и контент-модули

### 1. Reddit → Канал "Лучшее с Reddit"
- **Источник**: RSS subreddits + snoowraw API
- **Обработка**: AI-перевод (EN→RU), рерайт, адаптация
- **Частота**: каждые 30 минут
- **Фильтры**: NSFW, минимальный рейтинг, дубликаты
- **Медиа**: изображения, видео из Reddit

### 2. Гороскопы на каждый день
- **Источник**: Астрономические данные + шаблоны
- **Обработка**: GLM-5 генерация уникального текста
- **Частота**: ежедневно в 00:00
- **Формат**: 12 постов по знакам зодиака

### 3. Интересные факты о животных
- **Источник**: Wikipedia API + собственная база фактов
- **Обработка**: AI-рерайт, проверка достоверности
- **Частота**: 3-5 постов в день
- **Медиа**: Unsplash API для изображений

### 4. Новостной канал (с цензурой РФ)
- **Источник**: RSS (ТАСС, Интерфакс, РИА Новости)
- **Обработка**: AI-суммаризация + модуль цензуры
- **Частота**: каждые 15 минут
- **Особенности**: нейтральный тон, фильтрация запрещённых тем

### 5. Городские каналы
- **Источник**: OpenWeatherMap, локальные RSS, открытые API
- **Обработка**: компиляция контента (погода + события + новости)
- **Частота**: 2-3 поста в день
- **Гео**: мульти-город (Москва, СПб, и т.д.)

### 6. Реферальные каналы (товары)
- **Источник**: База товаров с реф-ссылками
- **Обработка**: AI-генерация native-постов, ненавязчивая встройка ссылок
- **Форматы**: обзоры, рекомендации, полезные советы
- **Аналитика**: трекинг кликов и конверсий

---

## Модуль цензуры (для РФ)

### Категории проверок
1. **Стоп-слова**: политика, протесты, спецоперации и т.д.
2. **Regex-паттерны**: имена политиков, названия организаций
3. **Контекстный анализ**: намёки, аллюзии через AI
4. **Проверка изображений**: OCR текста на картинках
5. **Проверка ссылок**: запрещённые домены

### Действия при срабатывании
- `auto_reject` — автоскрытие поста
- `auto_warn` — предупреждение модератору
- `manual_review` — обязательная ручная проверка
- `auto_edit` — автоматическая замена на безопасные слова

---

## Модель данных (PostgreSQL)

### Основные таблицы

```sql
-- Пользователи (только admin)
users: id, username, password_hash, is_active, created_at

-- Каналы
channels: id, name, type, platform, config(json), is_active, created_at

-- Типы контента
content_types: id, name, source_type, generator_config(json)

-- Связь каналов с типами контента
channel_content: channel_id, content_type_id, schedule(cron)

-- Посты
posts: id, channel_id, content_type_id, status(enum),
       title, body, media_urls(json),
       source_url, generated_at, published_at,
       censorship_flags(json), ai_metadata(json)

-- Очередь публикаций
publish_queue: id, post_id, scheduled_at, priority, attempts, status

-- Товары (реферальные)
affiliate_products: id, name, category, ref_url, description, keywords, is_active

-- Стоп-слова цензуры
censorship_rules: id, pattern, type(enum: banned/warn/review), category

-- Логи публикаций
publish_logs: id, post_id, platform, status, error_message, timestamp

-- Аналитика
analytics: id, post_id, platform, views, likes, shares, clicks, date
```

### Статусы постов
```
draft → pending → approved → scheduled → published → failed
                  ↓
                rejected
```

---

## API интеграции

### Telegram Bot API
- Публикация в каналы
- Markdown/HTML форматирование
- Медиа: photo, video, documents
- Inline-кнопки для реф-ссылок

### VK API
- wall.post для пабликов
- VK Markets для товаров
- Вложения: фото, видео, ссылки

### WordPress REST API
- Создание постов
- Категории и теги
- SEO-поля (meta description, title)
- Featured Image

### Unsplash API
- Поиск изображений по ключевым словам
- Автоподбор к постам
- Free лицензия

### OpenWeatherMap API
- Погода для городских каналов
- Прогнозы

---

## Функционал Dashboard

### 1. Каналы
- CRUD каналов
- Настройка платформ (API токены)
- Привязка контент-модулей
- Статистика по каналу

### 2. Очередь постов
- Календарь публикаций
- Список с фильтрами (статус, канал, дата)
- Действия: edit, approve, reject, reschedule
- Массовые операции
- Предпросмотр для каждой платформы

### 3. Редактор поста
- Markdown editor
- Загрузка медиа
- AI-помощник (улучшить, сократить, рерайт)
- Real-time проверка цензуры
- Предпросмотр

### 4. Контент-модули
- Настройка источников
- Параметры генерации
- Тестовая генерация
- Шаблоны промптов

### 5. Товары (реферальные)
- База товаров
- Категоризация
- Статистика кликов
- Связь с каналами

### 6. Аналитика
- Графики просмотров/вовлечённости
- Топ постов
- Лучшее время постинга
- ROI по реф-ссылкам

### 7. Настройки
- API ключи (Telegram, VK, WP, GLM-5, Unsplash)
- Цензура: стоп-слова, правила
- Расписания
- Уведомления (Telegram alerts)

---

## UI/UX

- **Тема**: тёмная (dark mode)
- **Фреймворк**: TailwindCSS
- **Компоненты**: кастомные + Headless UI
- **Адаптив**: desktop-first (admin panel)

---

## Планировщик (Celery Beat)

```python
SCHEDULES = {
    'reddit_fetch': crontab(minute='*/30'),
    'horoscope_generate': crontab(hour=0, minute=0),
    'animal_facts_generate': crontab(hour='8,14,20', minute=0),
    'news_fetch': crontab(minute='*/15'),
    'city_content_generate': crontab(hour='7,13,19', minute=0),
    'publish_scheduled': crontab(minute='*'),
    'analytics_collect': crontab(minute='*/30'),
    'cleanup_old_posts': crontab(hour=3, minute=0),
}
```

---

## Безопасность

- JWT авторизация (HS256)
- Bcrypt хеширование паролей
- Шифрование API ключей в БД (Fernet)
- Rate limiting (slowapi)
- CORS whitelist
- IP whitelist для админки (опционально)
- Daily backup БД
- Audit log действий

---

## Этапы разработки

### Этап 1: Foundation (2-3 дня)
- Структура проекта
- Docker Compose
- FastAPI backend core
- Vue 3 frontend skeleton
- JWT auth
- Базовый CRUD каналов

### Этап 2: Content Types & Channels (2-3 дня)
- Models: content_types, channel_content
- UI управления типами контента
- Связка канал ↔ тип контента

### Этап 3: Content Modules (5-7 дней)
- Reddit parser
- Horoscope generator
- Animal facts
- News parser
- City channels
- Affiliate products

### Этап 4: Censorship Module (2 дня)
- База правил
- AI-проверка
- UI управления

### Этап 5: Queue & Scheduler (2-3 дня)
- Celery setup
- Redis queue
- UI календарь

### Этап 6: Publishers (3-4 дня)
- Telegram Bot API
- VK API
- WordPress REST API

### Этап 7: Media & Assets (2 дня)
- Unsplash integration
- Media storage
- Image optimization

### Этап 8: Post Editor (2 дня)
- Markdown editor
- AI assistant
- Preview

### Этап 9: Analytics (2-3 дня)
- Data collection
- Dashboard charts
- Reports

### Этап 10: Settings & Polish (2 дня)
- Settings UI
- Error handling
- Responsive

### Этап 11: Deployment (1-2 дня)
- reg.ru VPS setup
- Nginx + SSL
- Monitoring

---

## Переменные окружения

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/autoposting

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# AI
GLM_API_KEY=your-glm-api-key
GLM_API_URL=https://api.z.ai/v1

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token

# VK
VK_ACCESS_TOKEN=your-vk-token
VK_GROUP_ID=123456

# WordPress
WP_URL=https://your-site.com
WP_USERNAME=admin
WP_PASSWORD=application-password

# Unsplash
UNSPLASH_ACCESS_KEY=your-access-key

# OpenWeatherMap
OPENWEATHER_API_KEY=your-api-key

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-password
```

---

## Итого

- **Срок**: ~25-30 дней
- **Результат**: полноценная платформа автопостинга
- **Масштабируемость**: легко добавить новые типы контента и платформы
