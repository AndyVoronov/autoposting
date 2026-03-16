<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-dark-100">Очередь публикаций</h1>
        <p class="text-dark-400 mt-1">Управление запланированными постами</p>
      </div>
    </div>

    <div class="grid grid-cols-4 gap-4 mb-8">
      <div class="card">
        <p class="text-dark-400 text-sm">Ожидают</p>
        <p class="text-2xl font-bold text-yellow-400">{{ queueStats.pending }}</p>
      </div>
      <div class="card">
        <p class="text-dark-400 text-sm">Опубликованы</p>
        <p class="text-2xl font-bold text-accent-400">{{ queueStats.published }}</p>
      </div>
      <div class="card">
        <p class="text-dark-400 text-sm">Ошибки</p>
        <p class="text-2xl font-bold text-red-400">{{ queueStats.failed }}</p>
      </div>
      <div class="card">
        <p class="text-dark-400 text-sm">Всего сегодня</p>
        <p class="text-2xl font-bold text-dark-100">{{ queueStats.today }}</p>
      </div>
    </div>

    <div class="card">
      <div v-if="loading" class="text-center py-8 text-dark-400">Загрузка...</div>
      
      <div v-else-if="queue.length === 0" class="text-center py-8 text-dark-400">
        Очередь пуста
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="item in queue"
          :key="item.id"
          class="flex items-center gap-4 p-4 bg-dark-700/50 rounded-lg"
        >
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <span :class="getStatusBadge(item.status)">
                {{ getStatusLabel(item.status) }}
              </span>
              <span class="text-dark-400 text-sm">{{ getPlatformLabel(item.platform) }}</span>
            </div>
            <p class="text-dark-100 text-sm">Пост #{{ item.post_id }}</p>
            <p class="text-dark-500 text-xs">
              Запланировано: {{ formatDate(item.scheduled_at) }}
            </p>
          </div>
          
          <div class="flex items-center gap-2">
            <span class="text-dark-400 text-sm">
              Попыток: {{ item.attempts }}/{{ item.max_attempts }}
            </span>
            
            <button
              v-if="item.status === 'pending'"
              @click="removeFromQueue(item.id)"
              class="text-dark-400 hover:text-red-400"
            >
              <TrashIcon class="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, reactive } from 'vue'
import api from '@/api'
import { format } from 'date-fns'
import { TrashIcon } from '@heroicons/vue/24/outline'

const loading = ref(true)
const queue = ref<any[]>([])

const queueStats = reactive({
  pending: 0,
  published: 0,
  failed: 0,
  today: 0,
})

onMounted(async () => {
  await fetchQueue()
})

async function fetchQueue() {
  loading.value = true
  try {
    const response = await api.get('/queue')
    queue.value = response.data
    
    queueStats.pending = queue.value.filter(q => q.status === 'pending').length
    queueStats.published = queue.value.filter(q => q.status === 'published').length
    queueStats.failed = queue.value.filter(q => q.status === 'failed').length
    
    const today = new Date().toDateString()
    queueStats.today = queue.value.filter(q => 
      new Date(q.created_at).toDateString() === today
    ).length
  } finally {
    loading.value = false
  }
}

async function removeFromQueue(id: number) {
  if (!confirm('Удалить из очереди?')) return
  await api.delete(`/queue/${id}`)
  queue.value = queue.value.filter(q => q.id !== id)
}

function formatDate(date: string): string {
  try {
    return format(new Date(date), 'dd.MM.yyyy HH:mm')
  } catch {
    return date
  }
}

function getStatusBadge(status: string): string {
  const badges: Record<string, string> = {
    pending: 'badge badge-warning',
    published: 'badge badge-success',
    failed: 'badge badge-danger',
  }
  return badges[status] || 'badge badge-neutral'
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: 'Ожидает',
    published: 'Опубликован',
    failed: 'Ошибка',
  }
  return labels[status] || status
}

function getPlatformLabel(platform: string): string {
  const labels: Record<string, string> = {
    telegram: 'Telegram',
    vk: 'VK',
    wordpress: 'WordPress',
  }
  return labels[platform] || platform
}
</script>
