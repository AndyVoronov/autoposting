<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <router-link to="/posts" class="text-dark-400 hover:text-dark-100">
          <ArrowLeftIcon class="w-5 h-5" />
        </router-link>
        <h1 class="text-2xl font-bold text-dark-100">
          {{ isNewPost ? 'Новый пост' : 'Редактирование поста' }}
        </h1>
      </div>
      <div class="flex items-center gap-3">
        <span :class="statusBadgeClass">{{ statusLabel }}</span>
        <button @click="savePost" class="btn btn-primary" :disabled="saving">
          {{ saving ? 'Сохранение...' : 'Сохранить' }}
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="space-y-6">
        <div class="card">
          <h3 class="font-semibold text-dark-100 mb-4">Основное</h3>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm text-dark-400 mb-1">Канал *</label>
              <select v-model="form.channel_id" class="input" required>
                <option :value="null" disabled>Выберите канал</option>
                <option v-for="channel in channels" :key="channel.id" :value="channel.id">
                  {{ channel.name }} ({{ platformLabel(channel.platform) }})
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm text-dark-400 mb-1">Заголовок</label>
              <input v-model="form.title" type="text" class="input" placeholder="Необязательно" />
            </div>

            <div>
              <label class="block text-sm text-dark-400 mb-1">Статус</label>
              <select v-model="form.status" class="input">
                <option value="draft">Черновик</option>
                <option value="pending">На модерации</option>
                <option value="approved">Одобрен</option>
              </select>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-semibold text-dark-100">Текст поста</h3>
            <span class="text-sm text-dark-500">{{ form.body.length }} символов</span>
          </div>

          <div class="flex flex-wrap gap-2 mb-3">
            <button @click="aiImprove" class="btn btn-secondary text-sm py-1" :disabled="aiLoading || !form.body">
              <SparklesIcon class="w-4 h-4 mr-1" />
              Улучшить
            </button>
            <button @click="aiShorten" class="btn btn-secondary text-sm py-1" :disabled="aiLoading || !form.body">
              <ArrowsPointingInIcon class="w-4 h-4 mr-1" />
              Сократить
            </button>
            <button @click="aiRewrite" class="btn btn-secondary text-sm py-1" :disabled="aiLoading || !form.body">
              <ArrowPathIcon class="w-4 h-4 mr-1" />
              Рерайт
            </button>
            <button @click="checkCensorship" class="btn btn-secondary text-sm py-1" :disabled="censorshipLoading || !form.body">
              <ShieldCheckIcon class="w-4 h-4 mr-1" />
              Цензура
            </button>
          </div>

          <textarea
            v-model="form.body"
            class="input h-64 font-mono text-sm"
            placeholder="Текст поста..."
            required
          ></textarea>

          <div v-if="censorshipResult" class="mt-3 p-3 rounded-lg" :class="censorshipResult.passed ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'">
            <div class="flex items-center gap-2 mb-2">
              <component :is="censorshipResult.passed ? CheckCircleIcon : ExclamationCircleIcon" 
                         :class="censorshipResult.passed ? 'text-green-400' : 'text-red-400'"
                         class="w-5 h-5" />
              <span :class="censorshipResult.passed ? 'text-green-400' : 'text-red-400'" class="font-medium">
                {{ censorshipResult.passed ? 'Цензура пройдена' : 'Обнаружены проблемы' }}
              </span>
            </div>
            <div v-if="censorshipResult.matched_rules?.length" class="text-sm text-dark-300">
              <p class="mb-1">Найдены совпадения:</p>
              <ul class="list-disc list-inside">
                <li v-for="rule in censorshipResult.matched_rules" :key="rule.pattern">
                  "{{ rule.pattern }}" — {{ rule.type }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="card">
          <h3 class="font-semibold text-dark-100 mb-4">Медиа</h3>
          <div>
            <label class="block text-sm text-dark-400 mb-1">URL изображений (по одному на строку)</label>
            <textarea
              v-model="form.mediaUrlsText"
              class="input h-24 font-mono text-sm"
              placeholder="https://example.com/image1.jpg&#10;https://example.com/image2.jpg"
            ></textarea>
          </div>
          <div v-if="mediaUrls.length" class="mt-3 grid grid-cols-4 gap-2">
            <div v-for="(url, index) in mediaUrls" :key="index" class="aspect-square rounded-lg overflow-hidden bg-dark-700">
              <img :src="url" class="w-full h-full object-cover" @error="($event.target as HTMLImageElement).style.display='none'" />
            </div>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <div class="card">
          <div class="flex items-center gap-2 mb-4">
            <button
              v-for="p in ['telegram', 'vk', 'wordpress']"
              :key="p"
              @click="previewPlatform = p"
              :class="previewPlatform === p ? 'btn btn-primary' : 'btn btn-secondary'"
              class="text-sm py-1"
            >
              {{ platformLabel(p) }}
            </button>
          </div>

          <div class="bg-dark-800 rounded-xl p-4 min-h-[400px]">
            <div v-if="previewPlatform === 'telegram'" class="space-y-3">
              <div class="flex items-center gap-2 text-dark-400 text-sm mb-4">
                <ChatBubbleLeftRightIcon class="w-4 h-4" />
                <span>Telegram Preview</span>
              </div>
              <div class="bg-dark-700 rounded-xl p-4">
                <p v-if="form.title" class="font-bold text-dark-100 mb-2">{{ form.title }}</p>
                <div class="text-dark-200 text-sm whitespace-pre-wrap">{{ form.body || 'Текст поста...' }}</div>
                <div v-if="mediaUrls.length" class="mt-3">
                  <img :src="mediaUrls[0]" class="rounded-lg max-h-64" />
                </div>
              </div>
            </div>

            <div v-else-if="previewPlatform === 'vk'" class="space-y-3">
              <div class="flex items-center gap-2 text-dark-400 text-sm mb-4">
                <ChatBubbleLeftRightIcon class="w-4 h-4" />
                <span>VK Preview</span>
              </div>
              <div class="bg-white rounded-xl p-4 text-gray-900">
                <p v-if="form.title" class="font-bold text-lg mb-2">{{ form.title }}</p>
                <div class="text-gray-700 text-sm whitespace-pre-wrap">{{ form.body || 'Текст поста...' }}</div>
                <div v-if="mediaUrls.length" class="mt-3 grid grid-cols-2 gap-2">
                  <img v-for="(url, i) in mediaUrls.slice(0, 4)" :key="i" :src="url" class="rounded w-full h-24 object-cover" />
                </div>
              </div>
            </div>

            <div v-else-if="previewPlatform === 'wordpress'" class="space-y-3">
              <div class="flex items-center gap-2 text-dark-400 text-sm mb-4">
                <GlobeAltIcon class="w-4 h-4" />
                <span>WordPress Preview</span>
              </div>
              <article class="prose prose-invert max-w-none">
                <h1 v-if="form.title" class="text-2xl font-bold text-dark-100 mb-4">{{ form.title }}</h1>
                <div class="text-dark-200 leading-relaxed whitespace-pre-wrap">{{ form.body || 'Текст поста...' }}</div>
                <div v-if="mediaUrls.length" class="mt-4">
                  <img :src="mediaUrls[0]" class="rounded-lg max-w-full" />
                </div>
              </article>
            </div>
          </div>
        </div>

        <div v-if="!isNewPost && post" class="card">
          <h3 class="font-semibold text-dark-100 mb-4">Информация</h3>
          <dl class="space-y-2 text-sm">
            <div class="flex justify-between">
              <dt class="text-dark-400">ID</dt>
              <dd class="text-dark-200">#{{ post.id }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-dark-400">Создан</dt>
              <dd class="text-dark-200">{{ formatDate(post.created_at) }}</dd>
            </div>
            <div v-if="post.published_at" class="flex justify-between">
              <dt class="text-dark-400">Опубликован</dt>
              <dd class="text-dark-200">{{ formatDate(post.published_at) }}</dd>
            </div>
            <div v-if="post.scheduled_at" class="flex justify-between">
              <dt class="text-dark-400">Запланирован</dt>
              <dd class="text-dark-200">{{ formatDate(post.scheduled_at) }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-dark-400">Цензура</dt>
              <dd :class="post.censorship_passed ? 'text-green-400' : 'text-yellow-400'">
                {{ post.censorship_passed ? 'Пройдена' : 'Не пройдена' }}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'
import { format } from 'date-fns'
import { useChannelsStore } from '@/stores/channels'
import { usePostsStore } from '@/stores/posts'
import type { Post, Channel } from '@/api/types'
import {
  ArrowLeftIcon,
  SparklesIcon,
  ArrowsPointingInIcon,
  ArrowPathIcon,
  ShieldCheckIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ChatBubbleLeftRightIcon,
  GlobeAltIcon,
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const channelsStore = useChannelsStore()
const postsStore = usePostsStore()

const isNewPost = computed(() => route.params.id === 'new' || !route.params.id)
const postId = computed(() => route.params.id ? Number(route.params.id) : null)

const channels = computed(() => channelsStore.channels)
const post = ref<Post | null>(null)
const saving = ref(false)
const aiLoading = ref(false)
const censorshipLoading = ref(false)
const censorshipResult = ref<any>(null)
const previewPlatform = ref<'telegram' | 'vk' | 'wordpress'>('telegram')

const form = reactive({
  channel_id: null as number | null,
  title: '',
  body: '',
  mediaUrlsText: '',
  status: 'draft' as string,
})

const mediaUrls = computed(() => {
  return form.mediaUrlsText
    .split('\n')
    .map(s => s.trim())
    .filter(Boolean)
})

const statusBadgeClass = computed(() => {
  const classes: Record<string, string> = {
    draft: 'badge badge-neutral',
    pending: 'badge badge-warning',
    approved: 'badge badge-success',
    scheduled: 'badge badge-info',
    published: 'badge badge-success',
    failed: 'badge badge-danger',
    rejected: 'badge badge-danger',
  }
  return classes[form.status] || 'badge badge-neutral'
})

const statusLabel = computed(() => {
  const labels: Record<string, string> = {
    draft: 'Черновик',
    pending: 'На модерации',
    approved: 'Одобрен',
    scheduled: 'Запланирован',
    published: 'Опубликован',
    failed: 'Ошибка',
    rejected: 'Отклонён',
  }
  return labels[form.status] || form.status
})

onMounted(async () => {
  await channelsStore.fetchChannels()
  
  if (!isNewPost.value && postId.value) {
    const data = await postsStore.fetchPost(postId.value)
    if (data) {
      post.value = data
      form.channel_id = data.channel_id
      form.title = data.title || ''
      form.body = data.body
      form.mediaUrlsText = data.media_urls?.join('\n') || ''
      form.status = data.status
      previewPlatform.value = data.channel_id ? getChannelPlatform(data.channel_id) : 'telegram'
    }
  }
})

function getChannelPlatform(channelId: number): 'telegram' | 'vk' | 'wordpress' {
  const channel = channels.value.find(c => c.id === channelId)
  return channel?.platform || 'telegram'
}

function platformLabel(platform: string): string {
  const labels: Record<string, string> = {
    telegram: 'Telegram',
    vk: 'VK',
    wordpress: 'WordPress',
  }
  return labels[platform] || platform
}

function formatDate(date: string): string {
  try {
    return format(new Date(date), 'dd.MM.yyyy HH:mm')
  } catch {
    return date
  }
}

async function savePost() {
  if (!form.channel_id || !form.body.trim()) {
    alert('Заполните обязательные поля')
    return
  }

  saving.value = true
  try {
    const data = {
      channel_id: form.channel_id,
      title: form.title || null,
      body: form.body,
      media_urls: mediaUrls.value.length ? mediaUrls.value : null,
      status: form.status,
    }

    if (isNewPost.value) {
      const created = await postsStore.createPost(data)
      router.push(`/posts/${created.id}`)
    } else if (postId.value) {
      await postsStore.updatePost(postId.value, data)
    }
  } catch (error) {
    alert('Ошибка сохранения')
  } finally {
    saving.value = false
  }
}

async function aiImprove() {
  if (!form.body.trim()) return
  aiLoading.value = true
  try {
    const response = await api.post('/ai/improve', { text: form.body })
    if (response.data.success && response.data.result) {
      form.body = response.data.result
    } else {
      alert('AI не смог обработать текст')
    }
  } catch (error) {
    alert('Ошибка AI')
  } finally {
    aiLoading.value = false
  }
}

async function aiShorten() {
  if (!form.body.trim()) return
  aiLoading.value = true
  try {
    const response = await api.post('/ai/shorten', { text: form.body, max_chars: 500 })
    if (response.data.success && response.data.result) {
      form.body = response.data.result
    } else {
      alert('AI не смог обработать текст')
    }
  } catch (error) {
    alert('Ошибка AI')
  } finally {
    aiLoading.value = false
  }
}

async function aiRewrite() {
  if (!form.body.trim()) return
  aiLoading.value = true
  try {
    const response = await api.post('/ai/rewrite', { text: form.body })
    if (response.data.success && response.data.result) {
      form.body = response.data.result
    } else {
      alert('AI не смог обработать текст')
    }
  } catch (error) {
    alert('Ошибка AI')
  } finally {
    aiLoading.value = false
  }
}

async function checkCensorship() {
  if (!form.body.trim()) return
  censorshipLoading.value = true
  try {
    const response = await api.post('/censorship/check', { text: form.body })
    censorshipResult.value = response.data
  } catch (error) {
    alert('Ошибка проверки цензуры')
  } finally {
    censorshipLoading.value = false
  }
}
</script>
