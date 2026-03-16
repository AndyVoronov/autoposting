#!/bin/bash
set -e

echo "=========================================="
echo "  DEPLOY AUTOPOSTING PLATFORM"
echo "=========================================="

export DEPLOY_DOMAIN="workonmychannel.ru"
export DEPLOY_DIR="/opt/autoposting"

echo ""
echo "[1/7] Обновление системы..."
apt update && apt upgrade -y

echo ""
echo "[2/7] Установка Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker root
fi

echo ""
echo "[3/7] Установка Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

echo ""
echo "[4/7] Создание директории проекта..."
mkdir -p $DEPLOY_DIR
mkdir -p $DEPLOY_DIR/ssl
mkdir -p $DEPLOY_DIR/backups
mkdir -p $DEPLOY_DIR/media

echo ""
echo "[5/7] Копирование файлов проекта..."
# Файлы должны быть уже скопированы в $DEPLOY_DIR

echo ""
echo "[6/7] Запуск контейнеров..."
cd $DEPLOY_DIR
docker-compose -f docker-compose.deploy.yml --env-file .env.prod up -d --build

echo ""
echo "[7/7] Ожидание запуска баз данных..."
sleep 10

echo ""
echo "=========================================="
echo "  ДЕПЛОЙ ЗАВЕРШЕН!"
echo "=========================================="
echo ""
echo "Сайт: http://$DEPLOY_DOMAIN"
echo "API: http://$DEPLOY_DOMAIN/api"
echo "API Docs: http://$DEPLOY_DOMAIN/api/docs"
echo ""
echo "Логин: admin"
echo "Пароль: (из .env.prod)"
echo ""
echo "Полезные команды:"
echo "  Логи:      docker-compose -f docker-compose.deploy.yml logs -f"
echo "  Рестарт:   docker-compose -f docker-compose.deploy.yml restart"
echo "  Стоп:      docker-compose -f docker-compose.deploy.yml down"
echo ""
