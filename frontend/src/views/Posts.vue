<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-dark-100">Посты</h1>
        <p class="text-dark-400 mt-1">Управление контентом</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        + Новый пост
      </button>
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
            <button @click="editPost(post)" class="btn btn-secondary text-sm py-1">
              Редактировать
            </button>
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

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" @click.self="closeModal">
      <div class="bg-dark-800 rounded-xl p-6 w-full max-w-2xl border border-dark-700 max-h-[90vh] overflow-y-auto">
        <h2 class="text-xl font-bold text-dark-100 mb-4">
          {{ editingPost ? 'Редактировать пост' : 'Новый пост' }}
        </h2>

        <form @submit.prevent="savePost" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Канал</label>
            <select v-model="form.channel_id" class="input" required>
              <option v-for="channel in channelsStore.channels" :key="channel.id" :value="channel.id">
                {{ channel.name }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Заголовок</label>
            <input v-model="form.title" type="text" class="input" />
          </div>

          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Текст</label>
            <textarea v-model="form.body" class="input h-48" required></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Медиа URL (по одному на строку)</label>
            <textarea v-model="form.mediaUrlsText" class="input h-20" placeholder="https://..."></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Статус</label>
            <select v-model="form.status" class="input">
              <option value="draft">Черновик</option>
              <option value="pending">На модерации</option>
              <option value="approved">Одобрен</option>
            </select>
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
import { usePostsStore } from '@/stores/posts'
import { useChannelsStore } from '@/stores/channels'
import type { Post } from '@/api/types'
import { format } from 'date-fns'

const postsStore = usePostsStore()
const channelsStore = useChannelsStore()

const showCreateModal = ref(false)
const saving = ref(false)
const editingPost = ref<Post | null>(null)

const filters = reactive({
  status: '',
  channel_id: '',
})

const form = reactive({
  channel_id: null as number | null,
  title: '',
  body: '',
  mediaUrlsText: '',
  status: 'draft' as any,
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

function editPost(post: Post) {
  editingPost.value = post
  form.channel_id = post.channel_id
  form.title = post.title || ''
  form.body = post.body
  form.mediaUrlsText = post.media_urls?.join('\n') || ''
  form.status = post.status
  showCreateModal.value = true
}

function closeModal() {
  showCreateModal.value = false
  editingPost.value = null
  form.channel_id = null
  form.title = ''
  form.body = ''
  form.mediaUrlsText = ''
  form.status = 'draft'
}

async function savePost() {
  if (!form.channel_id) return
  
  saving.value = true
  
  try {
    const data: Record<string, any> = {
      channel_id: form.channel_id,
      title: form.title || null,
      body: form.body,
      media_urls: form.mediaUrlsText ? form.mediaUrlsText.split('\n').filter(Boolean) : null,
      status: form.status,
    }
    
    if (editingPost.value) {
      await postsStore.updatePost(editingPost.value.id, data)
    } else {
      await postsStore.createPost(data)
    }
    
    closeModal()
  } catch (error) {
    alert('Error saving post')
  } finally {
    saving.value = false
  }
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
