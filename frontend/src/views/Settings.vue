<template>
  <div class="p-6">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-dark-100">Настройки</h1>
      <p class="text-dark-400 mt-1">Конфигурация платформы</p>
    </div>

    <!-- API Status -->
    <div class="card mb-8">
      <h3 class="font-semibold text-dark-100 mb-4">Статус интеграций</h3>
      
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div class="text-center p-4 bg-dark-700/50 rounded-lg">
          <component :is="settings.telegram_configured ? CheckCircleIcon : XCircleIcon" 
                     :class="settings.telegram_configured ? 'text-accent-400' : 'text-dark-500'"
                     class="w-8 h-8 mx-auto mb-2" />
          <p class="text-sm text-dark-300">Telegram</p>
        </div>
        
        <div class="text-center p-4 bg-dark-700/50 rounded-lg">
          <component :is="settings.vk_configured ? CheckCircleIcon : XCircleIcon"
                     :class="settings.vk_configured ? 'text-accent-400' : 'text-dark-500'"
                     class="w-8 h-8 mx-auto mb-2" />
          <p class="text-sm text-dark-300">VK</p>
        </div>
        
        <div class="text-center p-4 bg-dark-700/50 rounded-lg">
          <component :is="settings.wordpress_configured ? CheckCircleIcon : XCircleIcon"
                     :class="settings.wordpress_configured ? 'text-accent-400' : 'text-dark-500'"
                     class="w-8 h-8 mx-auto mb-2" />
          <p class="text-sm text-dark-300">WordPress</p>
        </div>
        
        <div class="text-center p-4 bg-dark-700/50 rounded-lg">
          <component :is="settings.ai_configured ? CheckCircleIcon : XCircleIcon"
                     :class="settings.ai_configured ? 'text-accent-400' : 'text-dark-500'"
                     class="w-8 h-8 mx-auto mb-2" />
          <p class="text-sm text-dark-300">AI (GLM-5)</p>
        </div>
        
        <div class="text-center p-4 bg-dark-700/50 rounded-lg">
          <component :is="settings.unsplash_configured ? CheckCircleIcon : XCircleIcon"
                     :class="settings.unsplash_configured ? 'text-accent-400' : 'text-dark-500'"
                     class="w-8 h-8 mx-auto mb-2" />
          <p class="text-sm text-dark-300">Unsplash</p>
        </div>
        
        <div class="text-center p-4 bg-dark-700/50 rounded-lg">
          <component :is="settings.openweather_configured ? CheckCircleIcon : XCircleIcon"
                     :class="settings.openweather_configured ? 'text-accent-400' : 'text-dark-500'"
                     class="w-8 h-8 mx-auto mb-2" />
          <p class="text-sm text-dark-300">Weather</p>
        </div>
      </div>
    </div>

    <!-- API Keys -->
    <div class="card mb-8">
      <h3 class="font-semibold text-dark-100 mb-4">API ключи</h3>
      <p class="text-dark-400 text-sm mb-4">
        Настройки хранятся в файле .env на сервере. Для изменения отредактируйте файл и перезапустите сервисы.
      </p>

      <div class="space-y-4">
        <div class="p-4 bg-dark-700/50 rounded-lg">
          <div class="flex items-center justify-between mb-2">
            <span class="text-dark-300">Telegram Bot Token</span>
            <span :class="settings.telegram_configured ? 'text-accent-400' : 'text-dark-500'" class="text-sm">
              {{ settings.telegram_configured ? 'Настроен' : 'Не настроен' }}
            </span>
          </div>
          <p class="text-dark-500 text-sm font-mono">
            {{ settings.telegram_configured ? '••••••••••••••••' : 'Не указан' }}
          </p>
        </div>

        <div class="p-4 bg-dark-700/50 rounded-lg">
          <div class="flex items-center justify-between mb-2">
            <span class="text-dark-300">GLM-5 API Key</span>
            <span :class="settings.ai_configured ? 'text-accent-400' : 'text-dark-500'" class="text-sm">
              {{ settings.ai_configured ? 'Настроен' : 'Не настроен' }}
            </span>
          </div>
          <p class="text-dark-500 text-sm font-mono">
            {{ settings.ai_configured ? '••••••••••••••••' : 'Не указан' }}
          </p>
        </div>

        <div class="p-4 bg-dark-700/50 rounded-lg">
          <div class="flex items-center justify-between mb-2">
            <span class="text-dark-300">WordPress</span>
            <span :class="settings.wordpress_configured ? 'text-accent-400' : 'text-dark-500'" class="text-sm">
              {{ settings.wordpress_configured ? 'Настроен' : 'Не настроен' }}
            </span>
          </div>
          <p class="text-dark-500 text-sm">
            {{ settings.wordpress_configured ? 'URL, логин и пароль указаны' : 'Не указаны учётные данные' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="card">
      <h3 class="font-semibold text-dark-100 mb-4">Быстрые действия</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button class="btn btn-secondary text-left justify-start">
          <ArrowPathIcon class="w-5 h-5 mr-2" />
          Перезапустить Celery
        </button>
        
        <button class="btn btn-secondary text-left justify-start">
          <DocumentArrowDownIcon class="w-5 h-5 mr-2" />
          Экспорт данных
        </button>
        
        <button class="btn btn-secondary text-left justify-start">
          <TrashIcon class="w-5 h-5 mr-2" />
          Очистить логи
        </button>
        
        <button class="btn btn-secondary text-left justify-start">
          <ServerIcon class="w-5 h-5 mr-2" />
          Состояние сервера
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import api from '@/api'
import {
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  DocumentArrowDownIcon,
  TrashIcon,
  ServerIcon,
} from '@heroicons/vue/24/outline'

const settings = ref({
  telegram_configured: false,
  vk_configured: false,
  wordpress_configured: false,
  ai_configured: false,
  unsplash_configured: false,
  openweather_configured: false,
})

onMounted(async () => {
  try {
    const response = await api.get('/settings')
    settings.value = response.data
  } catch (error) {
    console.error('Failed to load settings')
  }
})
</script>
