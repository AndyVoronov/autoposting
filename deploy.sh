#!/bin/bash

# Deployment script for Autoposting platform
# Usage: ./deploy.sh [production|staging]

set -e

ENV=${1:-production}
echo "🚀 Deploying Autoposting ($ENV environment)..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Copy .env.example and configure it first."
    exit 1
fi

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Pull Docker images and rebuild
echo "🐳 Building Docker images..."
docker-compose build --no-cache

# Stop old containers
echo "🛑 Stopping old containers..."
docker-compose down

# Start new containers
echo "🚀 Starting containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services..."
sleep 10

# Check health
echo "🏥 Checking health..."
curl -f http://localhost/api/health || echo "⚠️ API health check failed"

# Done
echo "✅ Deployment complete!"
echo ""
echo "Dashboard: http://localhost"
echo "API Docs:  http://localhost/api/docs"
