<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-dark-100">Посты</h1>
        <p class="text-dark-400 mt-1">Управление контентом</p>
      </div>
      <router-link to="/posts/new" class="btn btn-primary">
        + Новый пост
      </router-link>
    </div>

    <!-- Filters -->
    <div class="card mb-6">
      <div class="flex flex-wrap gap-4">
        <select v-model="filters.status" class="input w-auto" @change="applyFilters">
          <option value="">Все статусы</option>
          <option value="draft">Черновики</option>
          <option value="pending">Ожидает</option>
          <option value="approved">Одобрены</option>
          <option value="scheduled">Запланированы</option>
          <option value="published">Опубликованы</option>
          <option value="rejected">Отклонены</option>
        </select>
        
        <select v-model="filters.channel_id" class="input w-auto" @change="applyFilters">
          <option value="">Все каналы</option>
          <option v-for="channel in channelsStore.channels" :key="channel.id" :value="channel.id">
            {{ channel.name }}
          </option>
        </select>
      </div>
    </div>

    <div v-if="postsStore.loading" class="text-center py-12 text-dark-400">
      Загрузка...
    </div>

    <div v-else-if="postsStore.posts.length === 0" class="text-center py-12">
      <div class="text-dark-400 mb-4">Нет постов</div>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="post in postsStore.posts"
        :key="post.id"
        class="card hover:border-dark-600 transition-colors"
      >
        <div class="flex gap-4">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <span :class="statusBadgeClass(post.status)">
                {{ statusLabel(post.status) }}
              </span>
              <span v-if="!post.censorship_passed" class="badge badge-warning">
                ⚠ Цензура
              </span>
            </div>
            
            <h3 class="font-semibold text-dark-100 mb-1">
              {{ post.title || 'Без заголовка' }}
            </h3>
            
            <p class="text-dark-400 text-sm line-clamp-2 mb-3">
              {{ post.body }}
            </p>

            <div class="flex items-center gap-4 text-xs text-dark-500">
              <span>Канал: {{ getChannelName(post.channel_id) }}</span>
              <span>Создан: {{ formatDate(post.created_at) }}</span>
            </div>
          </div>

          <div class="flex flex-col gap-2">
            <router-link :to="`/posts/${post.id}`" class="btn btn-secondary text-sm py-1 text-center">
              Редактировать
            </router-link>
            <button 
              v-if="post.status === 'pending'"
              @click="approvePost(post.id)"
              class="btn btn-success text-sm py-1"
            >
              Одобрить
            </button>
            <button 
              v-if="post.status === 'pending'"
              @click="rejectPost(post.id)"
              class="btn btn-danger text-sm py-1"
            >
              Отклонить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { usePostsStore } from '@/stores/posts'
import { useChannelsStore } from '@/stores/channels'
import { format } from 'date-fns'

const postsStore = usePostsStore()
const channelsStore = useChannelsStore()

const filters = reactive({
  status: '',
  channel_id: '',
})

onMounted(async () => {
  await channelsStore.fetchChannels()
  await applyFilters()
})

async function applyFilters() {
  const params: Record<string, any> = {}
  if (filters.status) params.status = filters.status
  if (filters.channel_id) params.channel_id = filters.channel_id
  await postsStore.fetchPosts(params)
}

function getChannelName(channelId: number): string {
  const channel = channelsStore.channels.find(c => c.id === channelId)
  return channel?.name || 'Unknown'
}

function formatDate(date: string): string {
  try {
    return format(new Date(date), 'dd.MM.yyyy HH:mm')
  } catch {
    return date
  }
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    draft: 'Черновик',
    pending: 'Ожидает',
    approved: 'Одобрен',
    scheduled: 'Запланирован',
    published: 'Опубликован',
    failed: 'Ошибка',
    rejected: 'Отклонён',
  }
  return labels[status] || status
}

function statusBadgeClass(status: string): string {
  const classes: Record<string, string> = {
    draft: 'badge badge-neutral',
    pending: 'badge badge-warning',
    approved: 'badge badge-info',
    scheduled: 'badge badge-info',
    published: 'badge badge-success',
    failed: 'badge badge-danger',
    rejected: 'badge badge-danger',
  }
  return classes[status] || 'badge badge-neutral'
}

async function approvePost(id: number) {
  await postsStore.approvePost(id)
}

async function rejectPost(id: number) {
  if (confirm('Отклонить этот пост?')) {
    await postsStore.rejectPost(id)
  }
}
</script>
