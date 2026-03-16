<template>
  <div class="min-h-screen bg-dark-900 flex">
    <!-- Sidebar -->
    <aside class="w-64 bg-dark-800 border-r border-dark-700 flex flex-col">
      <div class="p-4 border-b border-dark-700">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
            <span class="text-xl font-bold text-white">A</span>
          </div>
          <div>
            <h1 class="font-bold text-dark-100">Autoposting</h1>
            <p class="text-xs text-dark-400">v0.1.0</p>
          </div>
        </div>
      </div>

      <nav class="flex-1 p-4 space-y-1">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-dark-300 hover:text-dark-100 hover:bg-dark-700 transition-colors"
          :class="{ 'bg-dark-700 text-dark-100': $route.path === item.path }"
        >
          <component :is="item.icon" class="w-5 h-5" />
          <span>{{ item.name }}</span>
        </router-link>
      </nav>

      <div class="p-4 border-t border-dark-700">
        <div class="flex items-center gap-3 px-3 py-2">
          <div class="w-8 h-8 rounded-full bg-dark-600 flex items-center justify-center">
            <span class="text-sm font-medium">{{ userInitial }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-dark-100 truncate">{{ authStore.user?.username }}</p>
          </div>
          <button
            @click="logout"
            class="text-dark-400 hover:text-dark-100 transition-colors"
          >
            <ArrowRightOnRectangleIcon class="w-5 h-5" />
          </button>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 overflow-auto">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  HomeIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  ClockIcon,
  CogIcon,
  SparklesIcon,
  ShoppingBagIcon,
  ShieldExclamationIcon,
  ChartBarIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()

const menuItems = [
  { name: 'Дашборд', path: '/', icon: HomeIcon },
  { name: 'Каналы', path: '/channels', icon: ChatBubbleLeftRightIcon },
  { name: 'Посты', path: '/posts', icon: DocumentTextIcon },
  { name: 'Очередь', path: '/queue', icon: ClockIcon },
  { name: 'Типы контента', path: '/content', icon: SparklesIcon },
  { name: 'Товары', path: '/products', icon: ShoppingBagIcon },
  { name: 'Цензура', path: '/censorship', icon: ShieldExclamationIcon },
  { name: 'Аналитика', path: '/analytics', icon: ChartBarIcon },
  { name: 'Настройки', path: '/settings', icon: CogIcon },
]

const userInitial = computed(() => {
  return authStore.user?.username?.charAt(0).toUpperCase() || 'A'
})

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>
