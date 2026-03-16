<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-dark-100">Каналы</h1>
        <p class="text-dark-400 mt-1">Управление каналами публикации</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        + Добавить канал
      </button>
    </div>

    <div v-if="channelsStore.loading" class="text-center py-12 text-dark-400">
      Загрузка...
    </div>

    <div v-else-if="channelsStore.channels.length === 0" class="text-center py-12">
      <div class="text-dark-400 mb-4">Нет каналов</div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        Создать первый канал
      </button>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="channel in channelsStore.channels"
        :key="channel.id"
        class="card hover:border-dark-600 transition-colors cursor-pointer"
        @click="editChannel(channel)"
      >
        <div class="flex items-start justify-between mb-3">
          <div class="flex items-center gap-3">
            <div :class="platformIconBg(channel.platform)" class="w-10 h-10 rounded-lg flex items-center justify-center">
              <component :is="platformIcon(channel.platform)" class="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 class="font-semibold text-dark-100">{{ channel.name }}</h3>
              <p class="text-sm text-dark-400">{{ channel.slug }}</p>
            </div>
          </div>
          <span :class="channel.is_active ? 'badge badge-success' : 'badge badge-neutral'">
            {{ channel.is_active ? 'Активен' : 'Отключен' }}
          </span>
        </div>
        
        <div class="flex items-center justify-between text-sm">
          <span class="text-dark-400">{{ platformLabel(channel.platform) }}</span>
          <span class="text-dark-500">ID: {{ channel.id }}</span>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="closeModal">
      <div class="bg-dark-800 rounded-xl p-6 w-full max-w-md border border-dark-700">
        <h2 class="text-xl font-bold text-dark-100 mb-4">
          {{ editingChannel ? 'Редактировать канал' : 'Новый канал' }}
        </h2>

        <form @submit.prevent="saveChannel" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Название</label>
            <input v-model="form.name" type="text" class="input" required />
          </div>

          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Slug</label>
            <input v-model="form.slug" type="text" class="input" required placeholder="my-channel" />
          </div>

          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Платформа</label>
            <select v-model="form.platform" class="input">
              <option value="telegram">Telegram</option>
              <option value="vk">VK</option>
              <option value="wordpress">WordPress</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Конфигурация (JSON)</label>
            <textarea v-model="form.configJson" class="input h-24 font-mono text-sm" placeholder='{"token": "..."}'></textarea>
          </div>

          <div class="flex items-center gap-2">
            <input v-model="form.is_active" type="checkbox" id="is_active" class="rounded" />
            <label for="is_active" class="text-sm text-dark-300">Активен</label>
          </div>

          <div class="flex gap-3 pt-4">
            <button type="button" @click="closeModal" class="btn btn-secondary flex-1">
              Отмена
            </button>
            <button type="submit" class="btn btn-primary flex-1" :disabled="saving">
              {{ saving ? 'Сохранение...' : 'Сохранить' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useChannelsStore } from '@/stores/channels'
import type { Channel } from '@/api/types'
import {
  ChatBubbleLeftRightIcon,
  GlobeAltIcon,
  DocumentTextIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const channelsStore = useChannelsStore()

const showCreateModal = ref(false)
const saving = ref(false)
const editingChannel = ref<Channel | null>(null)

const form = reactive({
  name: '',
  slug: '',
  platform: 'telegram' as 'telegram' | 'vk' | 'wordpress',
  configJson: '',
  is_active: true,
})

onMounted(() => {
  channelsStore.fetchChannels()
})

function platformIcon(platform: string) {
  const icons: Record<string, any> = {
    telegram: ChatBubbleLeftRightIcon,
    vk: ChatBubbleLeftRightIcon,
    wordpress: GlobeAltIcon,
  }
  return icons[platform] || DocumentTextIcon
}

function platformIconBg(platform: string): string {
  const bgs: Record<string, string> = {
    telegram: 'bg-blue-500',
    vk: 'bg-sky-500',
    wordpress: 'bg-blue-600',
  }
  return bgs[platform] || 'bg-dark-600'
}

function platformLabel(platform: string): string {
  const labels: Record<string, string> = {
    telegram: 'Telegram',
    vk: 'ВКонтакте',
    wordpress: 'WordPress',
  }
  return labels[platform] || platform
}

function editChannel(channel: Channel) {
  editingChannel.value = channel
  form.name = channel.name
  form.slug = channel.slug
  form.platform = channel.platform
  form.configJson = channel.config ? JSON.stringify(channel.config, null, 2) : ''
  form.is_active = channel.is_active
  showCreateModal.value = true
}

function closeModal() {
  showCreateModal.value = false
  editingChannel.value = null
  form.name = ''
  form.slug = ''
  form.platform = 'telegram'
  form.configJson = ''
  form.is_active = true
}

async function saveChannel() {
  saving.value = true
  
  try {
    const data: Record<string, any> = {
      name: form.name,
      slug: form.slug,
      platform: form.platform,
      is_active: form.is_active,
    }
    
    if (form.configJson) {
      try {
        data.config = JSON.parse(form.configJson)
      } catch (e) {
        alert('Invalid JSON in config')
        saving.value = false
        return
      }
    }
    
    if (editingChannel.value) {
      await channelsStore.updateChannel(editingChannel.value.id, data)
    } else {
      await channelsStore.createChannel(data)
    }
    
    closeModal()
  } catch (error) {
    alert('Error saving channel')
  } finally {
    saving.value = false
  }
}
</script>
