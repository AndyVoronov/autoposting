# Инструкция по деплою

## Подготовка (одноразово)

### 1. Подключение к серверу
```bash
ssh root@89.111.175.54
# Пароль: hwEOYO2hzemBVA8F
```

### 2. Установка базового ПО
```bash
apt update && apt upgrade -y
apt install -y git curl
```

### 3. Установка Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

---

## Деплой

### Вариант А: Через Git (рекомендуется)

```bash
# На сервере
cd /opt
git clone <ваш-репозиторий> autoposting
cd autoposting
```

Создайте `.env.prod` на сервере:
```bash
nano .env.prod
# Вставьте содержимое из .env.prod локально
```

Запуск:
```bash
docker-compose -f deploy/docker-compose.deploy.yml --env-file .env.prod up -d --build
```

### Вариант Б: Через SCP (ручная загрузка)

С локального компьютера:
```bash
# Упаковать проект (без node_modules и venv)
tar --exclude='node_modules' --exclude='venv' --exclude='__pycache__' --exclude='.git' -czvf autoposting.tar.gz .

# Загрузить на сервер
scp autoposting.tar.gz root@89.111.175.54:/opt/

# Загрузить .env.prod
scp .env.prod root@89.111.175.54:/opt/autoposting/
```

На сервере:
```bash
cd /opt
mkdir -p autoposting
tar -xzvf autoposting.tar.gz -C autoposting
cd autoposting
docker-compose -f deploy/docker-compose.deploy.yml --env-file .env.prod up -d --build
```

---

## Проверка

```bash
# Статус контейнеров
docker-compose -f deploy/docker-compose.deploy.yml ps

# Логи
docker-compose -f deploy/docker-compose.deploy.yml logs -f

# Логи конкретного сервиса
docker-compose -f deploy/docker-compose.deploy.yml logs -f api
```

---

## Полезные команды

```bash
# Рестарт
docker-compose -f deploy/docker-compose.deploy.yml restart

# Остановить
docker-compose -f deploy/docker-compose.deploy.yml down

# Пересобрать
docker-compose -f deploy/docker-compose.deploy.yml up -d --build

# Зайти в контейнер
docker exec -it autoposting-api-1 bash

# Бэкап БД
docker exec autoposting-db-1 pg_dump -U autoposting autoposting > backup.sql
```

---

## SSL (HTTPS) - после первого деплоя

```bash
# Установка certbot
apt install -y certbot

# Получение сертификата
certbot certonly --standalone -d workonmychannel.ru -d www.workonmychannel.ru

# Копирование сертификатов
cp /etc/letsencrypt/live/workonmychannel.ru/fullchain.pem /opt/autoposting/ssl/
cp /etc/letsencrypt/live/workonmychannel.ru/privkey.pem /opt/autoposting/ssl/

# Переключение на HTTPS
# Заменить nginx.deploy.conf на nginx.prod.conf в docker-compose.deploy.yml
# Перезапустить nginx
docker-compose -f deploy/docker-compose.deploy.yml restart nginx
```
