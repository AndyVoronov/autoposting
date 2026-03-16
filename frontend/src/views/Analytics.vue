<template>
  <div class="p-6">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-dark-100">Аналитика</h1>
      <p class="text-dark-400 mt-1">Статистика и отчёты</p>
    </div>

    <!-- Stats cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="card">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
            <DocumentTextIcon class="w-5 h-5 text-primary-400" />
          </div>
          <div>
            <p class="text-dark-400 text-sm">Всего постов</p>
            <p class="text-xl font-bold text-dark-100">{{ stats.total_posts }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-yellow-500/20 flex items-center justify-center">
            <ClockIcon class="w-5 h-5 text-yellow-400" />
          </div>
          <div>
            <p class="text-dark-400 text-sm">В очереди</p>
            <p class="text-xl font-bold text-dark-100">{{ stats.pending_posts }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-accent-500/20 flex items-center justify-center">
            <EyeIcon class="w-5 h-5 text-accent-400" />
          </div>
          <div>
            <p class="text-dark-400 text-sm">Просмотров</p>
            <p class="text-xl font-bold text-dark-100">{{ formatNumber(stats.total_views) }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
            <CursorArrowClickIcon class="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <p class="text-dark-400 text-sm">Кликов</p>
            <p class="text-xl font-bold text-dark-100">{{ formatNumber(stats.total_clicks) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Daily posts chart -->
      <div class="card">
        <h3 class="font-semibold text-dark-100 mb-4">Посты за неделю</h3>
        <div class="h-64 flex items-end gap-2">
          <div
            v-for="(day, index) in dailyStats"
            :key="index"
            class="flex-1 flex flex-col items-center"
          >
            <div
              class="w-full bg-primary-500/80 rounded-t transition-all hover:bg-primary-400"
              :style="{ height: getBarHeight(day.posts, maxPosts) + 'px' }"
              :title="`${day.posts} постов`"
            ></div>
            <span class="text-xs text-dark-400 mt-2">{{ day.label }}</span>
          </div>
        </div>
      </div>

      <!-- Views chart -->
      <div class="card">
        <h3 class="font-semibold text-dark-100 mb-4">Просмотры за неделю</h3>
        <div class="h-64 flex items-end gap-2">
          <div
            v-for="(day, index) in dailyStats"
            :key="index"
            class="flex-1 flex flex-col items-center"
          >
            <div
              class="w-full bg-accent-500/80 rounded-t transition-all hover:bg-accent-400"
              :style="{ height: getBarHeight(day.views, maxViews) + 'px' }"
              :title="`${formatNumber(day.views)} просмотров`"
            ></div>
            <span class="text-xs text-dark-400 mt-2">{{ day.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Top posts -->
    <div class="card">
      <h3 class="font-semibold text-dark-100 mb-4">Топ постов по просмотрам</h3>
      
      <div v-if="loading" class="text-center py-8 text-dark-400">Загрузка...</div>
      
      <div v-else-if="topPosts.length === 0" class="text-center py-8 text-dark-400">
        Пока нет данных
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="(post, index) in topPosts"
          :key="post.id"
          class="flex items-center gap-4 p-3 bg-dark-700/50 rounded-lg"
        >
          <div
            class="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold"
            :class="{
              'bg-yellow-500 text-dark-900': index === 0,
              'bg-gray-400 text-dark-900': index === 1,
              'bg-amber-700 text-dark-900': index === 2,
              'bg-dark-600 text-dark-300': index > 2,
            }"
          >
            {{ index + 1 }}
          </div>
          
          <div class="flex-1 min-w-0">
            <p class="text-dark-100 truncate">{{ post.title || 'Без заголовка' }}</p>
            <p class="text-sm text-dark-400">{{ post.channel_name || post.platform }}</p>
          </div>
          
          <div class="text-right">
            <p class="text-lg font-bold text-dark-100">{{ formatNumber(post.views) }}</p>
            <p class="text-xs text-dark-400">просмотров</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import api from '@/api'
import {
  DocumentTextIcon,
  ClockIcon,
  EyeIcon,
  CursorArrowClickIcon,
} from '@heroicons/vue/24/outline'

const loading = ref(true)
const stats = ref({
  total_channels: 0,
  total_posts: 0,
  pending_posts: 0,
  published_today: 0,
  total_views: 0,
  total_clicks: 0,
})

const dailyStats = ref<any[]>([])
const topPosts = ref<any[]>([])

const maxPosts = computed(() => Math.max(...dailyStats.value.map(d => d.posts), 1))
const maxViews = computed(() => Math.max(...dailyStats.value.map(d => d.views), 1))

onMounted(async () => {
  await Promise.all([
    fetchDashboard(),
    fetchDailyStats(),
    fetchTopPosts(),
  ])
  loading.value = false
})

async function fetchDashboard() {
  try {
    const response = await api.get('/analytics/dashboard')
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch dashboard')
  }
}

async function fetchDailyStats() {
  try {
    const response = await api.get('/analytics/daily')
    dailyStats.value = response.data
  } catch (error) {
    // Generate mock data for demo
    const days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    dailyStats.value = days.map(label => ({
      label,
      posts: Math.floor(Math.random() * 10) + 1,
      views: Math.floor(Math.random() * 5000) + 500,
      clicks: Math.floor(Math.random() * 100) + 10,
    }))
  }
}

async function fetchTopPosts() {
  try {
    const response = await api.get('/analytics/top-posts')
    topPosts.value = response.data
  } catch (error) {
    // Mock data for demo
    topPosts.value = [
      { id: 1, title: 'Интересный факт о котах', views: 12350, platform: 'telegram', channel_name: 'Лучшее с Reddit' },
      { id: 2, title: 'Гороскоп на сегодня: Овен', views: 8920, platform: 'telegram', channel_name: 'Гороскопы' },
      { id: 3, title: 'Погода в Москве', views: 6540, platform: 'vk', channel_name: 'Москва' },
      { id: 4, title: 'ТОП-10 товаров для здоровья', views: 4320, platform: 'telegram', channel_name: 'Здоровье' },
      { id: 5, title: 'Новости технологий', views: 3180, platform: 'wordpress', channel_name: 'Tech News' },
    ]
  }
}

function formatNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

function getBarHeight(value: number, max: number): number {
  const minHeight = 10
  const maxHeight = 200
  if (max === 0) return minHeight
  return Math.max(minHeight, (value / max) * maxHeight)
}
</script>
