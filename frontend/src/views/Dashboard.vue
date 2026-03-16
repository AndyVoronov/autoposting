<template>
  <div class="p-6">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-dark-100">Дашборд</h1>
      <p class="text-dark-400 mt-1">Обзор активности платформы</p>
    </div>

    <!-- Stats cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-dark-400 text-sm">Каналы</p>
            <p class="text-2xl font-bold text-dark-100 mt-1">{{ stats.channels }}</p>
          </div>
          <div class="w-12 h-12 rounded-xl bg-primary-500/20 flex items-center justify-center">
            <ChatBubbleLeftRightIcon class="w-6 h-6 text-primary-400" />
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-dark-400 text-sm">Постов в очереди</p>
            <p class="text-2xl font-bold text-dark-100 mt-1">{{ stats.pending }}</p>
          </div>
          <div class="w-12 h-12 rounded-xl bg-yellow-500/20 flex items-center justify-center">
            <ClockIcon class="w-6 h-6 text-yellow-400" />
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-dark-400 text-sm">Опубликовано сегодня</p>
            <p class="text-2xl font-bold text-dark-100 mt-1">{{ stats.publishedToday }}</p>
          </div>
          <div class="w-12 h-12 rounded-xl bg-accent-500/20 flex items-center justify-center">
            <CheckCircleIcon class="w-6 h-6 text-accent-400" />
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-dark-400 text-sm">Всего просмотров</p>
            <p class="text-2xl font-bold text-dark-100 mt-1">{{ formatNumber(stats.totalViews) }}</p>
          </div>
          <div class="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
            <EyeIcon class="w-6 h-6 text-blue-400" />
          </div>
        </div>
      </div>
    </div>

    <!-- Recent posts -->
    <div class="card">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-dark-100">Последние посты</h2>
        <router-link to="/posts" class="text-sm text-primary-400 hover:text-primary-300">
          Все посты →
        </router-link>
      </div>

      <div v-if="postsStore.loading" class="text-center py-8 text-dark-400">
        Загрузка...
      </div>

      <div v-else-if="postsStore.posts.length === 0" class="text-center py-8 text-dark-400">
        Нет постов
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="post in postsStore.posts.slice(0, 5)"
          :key="post.id"
          class="flex items-center gap-4 p-3 rounded-lg bg-dark-700/50 hover:bg-dark-700 transition-colors"
        >
          <div class="flex-1 min-w-0">
            <p class="text-dark-100 truncate">{{ post.title || 'Без заголовка' }}</p>
            <p class="text-sm text-dark-400 truncate">{{ post.body.substring(0, 100) }}...</p>
          </div>
          <span :class="statusBadgeClass(post.status)">
            {{ statusLabel(post.status) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { usePostsStore } from '@/stores/posts'
import { useChannelsStore } from '@/stores/channels'
import {
  ChatBubbleLeftRightIcon,
  ClockIcon,
  CheckCircleIcon,
  EyeIcon,
} from '@heroicons/vue/24/outline'
import type { Post } from '@/api/types'

const postsStore = usePostsStore()
const channelsStore = useChannelsStore()

const stats = ref({
  channels: 0,
  pending: 0,
  publishedToday: 0,
  totalViews: 0,
})

onMounted(async () => {
  await Promise.all([
    postsStore.fetchPosts(),
    channelsStore.fetchChannels(),
  ])
  
  stats.value.channels = channelsStore.channels.length
  stats.value.pending = postsStore.posts.filter(p => p.status === 'pending' || p.status === 'scheduled').length
  stats.value.publishedToday = postsStore.posts.filter(p => {
    if (p.status !== 'published' || !p.published_at) return false
    const today = new Date().toDateString()
    return new Date(p.published_at).toDateString() === today
  }).length
})

function formatNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
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
</script>
