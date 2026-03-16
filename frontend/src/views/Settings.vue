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
        <button @click="restartCelery" class="btn btn-secondary text-left justify-start" :disabled="actionLoading === 'restart'">
          <ArrowPathIcon class="w-5 h-5 mr-2" :class="actionLoading === 'restart' ? 'animate-spin' : ''" />
          {{ actionLoading === 'restart' ? 'Перезапуск...' : 'Перезапустить Celery' }}
        </button>
        
        <button @click="exportData" class="btn btn-secondary text-left justify-start" :disabled="actionLoading === 'export'">
          <DocumentArrowDownIcon class="w-5 h-5 mr-2" />
          {{ actionLoading === 'export' ? 'Экспорт...' : 'Экспорт данных' }}
        </button>
        
        <button @click="clearLogs" class="btn btn-secondary text-left justify-start" :disabled="actionLoading === 'clear'">
          <TrashIcon class="w-5 h-5 mr-2" />
          {{ actionLoading === 'clear' ? 'Очистка...' : 'Очистить логи' }}
        </button>
        
        <button @click="showStatusModal = true" class="btn btn-secondary text-left justify-start">
          <ServerIcon class="w-5 h-5 mr-2" />
          Состояние сервера
        </button>
      </div>
    </div>

    <!-- Toast notification -->
    <div v-if="toast.show" 
         class="fixed bottom-6 right-6 p-4 rounded-lg shadow-lg z-50 max-w-sm"
         :class="toast.type === 'success' ? 'bg-green-600' : toast.type === 'error' ? 'bg-red-600' : 'bg-blue-600'">
      <p class="text-white">{{ toast.message }}</p>
    </div>

    <!-- Status Modal -->
    <div v-if="showStatusModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showStatusModal = false">
      <div class="bg-dark-800 rounded-xl p-6 w-full max-w-md border border-dark-700">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-dark-100">Состояние сервера</h2>
          <button @click="showStatusModal = false" class="text-dark-400 hover:text-dark-100">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>

        <div v-if="statusLoading" class="text-center py-8 text-dark-400">
          Загрузка...
        </div>

        <div v-else-if="serverStatus" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="p-3 bg-dark-700/50 rounded-lg">
              <p class="text-dark-400 text-sm">CPU</p>
              <p class="text-xl font-bold" :class="serverStatus.cpu_percent > 80 ? 'text-red-400' : 'text-dark-100'">
                {{ serverStatus.cpu_percent.toFixed(1) }}%
              </p>
            </div>
            <div class="p-3 bg-dark-700/50 rounded-lg">
              <p class="text-dark-400 text-sm">Память</p>
              <p class="text-xl font-bold" :class="serverStatus.memory_percent > 80 ? 'text-red-400' : 'text-dark-100'">
                {{ serverStatus.memory_percent.toFixed(1) }}%
              </p>
            </div>
          </div>

          <div class="p-3 bg-dark-700/50 rounded-lg">
            <p class="text-dark-400 text-sm">Диск</p>
            <div class="flex items-center gap-3 mt-1">
              <div class="flex-1 h-2 bg-dark-600 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all"
                     :class="serverStatus.disk_percent > 80 ? 'bg-red-500' : 'bg-accent-500'"
                     :style="{ width: serverStatus.disk_percent + '%' }"></div>
              </div>
              <span class="text-dark-100 font-medium">{{ serverStatus.disk_percent.toFixed(1) }}%</span>
            </div>
          </div>

          <div class="space-y-2">
            <div class="flex items-center justify-between p-3 bg-dark-700/50 rounded-lg">
              <span class="text-dark-300">Celery</span>
              <span :class="getStatusColor(serverStatus.celery_status)" class="badge">
                {{ getStatusLabel(serverStatus.celery_status) }}
              </span>
            </div>
            <div class="flex items-center justify-between p-3 bg-dark-700/50 rounded-lg">
              <span class="text-dark-300">Redis</span>
              <span :class="getStatusColor(serverStatus.redis_status)" class="badge">
                {{ getStatusLabel(serverStatus.redis_status) }}
              </span>
            </div>
            <div class="flex items-center justify-between p-3 bg-dark-700/50 rounded-lg">
              <span class="text-dark-300">Database</span>
              <span :class="getStatusColor(serverStatus.database_status)" class="badge">
                {{ getStatusLabel(serverStatus.database_status) }}
              </span>
            </div>
          </div>

          <div class="p-3 bg-dark-700/50 rounded-lg">
            <p class="text-dark-400 text-sm">Uptime</p>
            <p class="text-dark-100 font-mono">{{ serverStatus.uptime }}</p>
          </div>
        </div>

        <div class="mt-6">
          <button @click="fetchServerStatus" class="btn btn-secondary w-full">
            <ArrowPathIcon class="w-4 h-4 mr-2" />
            Обновить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, reactive } from 'vue'
import api from '@/api'
import {
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  DocumentArrowDownIcon,
  TrashIcon,
  ServerIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline'

const settings = ref({
  telegram_configured: false,
  vk_configured: false,
  wordpress_configured: false,
  ai_configured: false,
  unsplash_configured: false,
  openweather_configured: false,
})

const actionLoading = ref<string | null>(null)
const showStatusModal = ref(false)
const statusLoading = ref(false)
const serverStatus = ref<any>(null)

const toast = reactive({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error' | 'info',
})

function showToast(message: string, type: 'success' | 'error' | 'info' = 'success') {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => {
    toast.show = false
  }, 3000)
}

onMounted(async () => {
  try {
    const response = await api.get('/settings')
    settings.value = response.data
  } catch (error) {
    console.error('Failed to load settings')
  }
})

async function restartCelery() {
  actionLoading.value = 'restart'
  try {
    const response = await api.post('/settings/restart-celery')
    showToast(response.data.message, 'success')
  } catch (error: any) {
    showToast(error.response?.data?.detail || 'Ошибка перезапуска', 'error')
  } finally {
    actionLoading.value = null
  }
}

async function exportData() {
  actionLoading.value = 'export'
  try {
    const response = await api.get('/settings/export')
    const data = JSON.stringify(response.data, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `autoposting-export-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
    showToast('Данные экспортированы', 'success')
  } catch (error) {
    showToast('Ошибка экспорта', 'error')
  } finally {
    actionLoading.value = null
  }
}

async function clearLogs() {
  if (!confirm('Удалить логи старше 30 дней?')) return
  
  actionLoading.value = 'clear'
  try {
    const response = await api.delete('/settings/logs', { params: { days: 30 } })
    const { deleted_publish_logs, deleted_censorship_logs, deleted_analytics } = response.data
    const total = deleted_publish_logs + deleted_censorship_logs + deleted_analytics
    showToast(`Удалено ${total} записей`, 'success')
  } catch (error) {
    showToast('Ошибка очистки', 'error')
  } finally {
    actionLoading.value = null
  }
}

async function fetchServerStatus() {
  statusLoading.value = true
  try {
    const response = await api.get('/settings/status')
    serverStatus.value = response.data
  } catch (error) {
    showToast('Ошибка получения статуса', 'error')
  } finally {
    statusLoading.value = false
  }
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    running: 'badge-success',
    error: 'badge-danger',
    unavailable: 'badge-warning',
    unknown: 'badge-neutral',
  }
  return colors[status] || 'badge-neutral'
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    running: 'Работает',
    error: 'Ошибка',
    unavailable: 'Недоступен',
    unknown: 'Неизвестно',
  }
  return labels[status] || status
}
</script>
