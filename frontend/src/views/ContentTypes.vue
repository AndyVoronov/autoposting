<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-dark-100">Типы контента</h1>
        <p class="text-dark-400 mt-1">Настройка источников и генераторов</p>
      </div>
    </div>

    <!-- Content type cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
      <div
        v-for="type in contentTypes"
        :key="type.id"
        class="card hover:border-dark-600 transition-colors cursor-pointer"
        @click="selectType(type)"
      >
        <div class="flex items-start justify-between mb-3">
          <div class="w-12 h-12 rounded-xl flex items-center justify-center" :class="getTypeColor(type.type)">
            <component :is="getTypeIcon(type.type)" class="w-6 h-6 text-white" />
          </div>
          <span :class="type.is_active ? 'badge badge-success' : 'badge badge-neutral'">
            {{ type.is_active ? 'Активен' : 'Отключен' }}
          </span>
        </div>
        
        <h3 class="font-semibold text-dark-100 mb-1">{{ type.name }}</h3>
        <p class="text-sm text-dark-400">{{ type.description || getTypeDescription(type.type) }}</p>
      </div>
    </div>

    <!-- Selected type details -->
    <div v-if="selectedType" class="card">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-lg font-semibold text-dark-100">{{ selectedType.name }}</h3>
        <button @click="closeEditor" class="text-dark-400 hover:text-dark-100">
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Reddit config -->
        <div v-if="selectedType.type === 'reddit'">
          <h4 class="font-medium text-dark-200 mb-3">Настройки Reddit</h4>
          <div class="space-y-3">
            <div>
              <label class="block text-sm text-dark-400 mb-1">Subreddits (по одному на строку)</label>
              <textarea v-model="form.config.subreddits" class="input h-24" placeholder="interestingasfuck&#10;todayilearned"></textarea>
            </div>
            <div>
              <label class="block text-sm text-dark-400 mb-1">Мин. рейтинг</label>
              <input type="number" v-model.number="form.config.min_score" class="input" />
            </div>
            <div class="flex items-center gap-4">
              <label class="flex items-center gap-2">
                <input type="checkbox" v-model="form.config.translate" class="rounded" />
                <span class="text-sm text-dark-300">Переводить</span>
              </label>
              <label class="flex items-center gap-2">
                <input type="checkbox" v-model="form.config.rewrite" class="rounded" />
                <span class="text-sm text-dark-300">Рерайтить</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Horoscope config -->
        <div v-else-if="selectedType.type === 'horoscope'">
          <h4 class="font-medium text-dark-200 mb-3">Настройки гороскопов</h4>
          <div class="space-y-3">
            <div>
              <label class="block text-sm text-dark-400 mb-1">Время публикации</label>
              <input type="time" v-model="form.config.publish_time" class="input" />
            </div>
            <div>
              <label class="block text-sm text-dark-400 mb-1">Знаки зодиака</label>
              <div class="grid grid-cols-3 gap-2">
                <label v-for="sign in zodiacSigns" :key="sign" class="flex items-center gap-2 text-sm text-dark-300">
                  <input type="checkbox" v-model="form.config.zodiac_signs" :value="sign" class="rounded" />
                  {{ sign }}
                </label>
              </div>
            </div>
            <label class="flex items-center gap-2">
              <input type="checkbox" v-model="form.config.use_ai" class="rounded" />
              <span class="text-sm text-dark-300">Использовать AI генерацию</span>
            </label>
          </div>
        </div>

        <!-- Animal Facts config -->
        <div v-else-if="selectedType.type === 'animal_facts'">
          <h4 class="font-medium text-dark-200 mb-3">Настройки фактов о животных</h4>
          <div class="space-y-3">
            <div>
              <label class="block text-sm text-dark-400 mb-1">Постов в день</label>
              <input type="number" v-model.number="form.config.posts_per_day" class="input" min="1" max="10" />
            </div>
            <label class="flex items-center gap-2">
              <input type="checkbox" v-model="form.config.use_ai" class="rounded" />
              <span class="text-sm text-dark-300">Использовать AI для рерайта</span>
            </label>
          </div>
        </div>

        <!-- News config -->
        <div v-else-if="selectedType.type === 'news'">
          <h4 class="font-medium text-dark-200 mb-3">Настройки новостей</h4>
          <div class="space-y-3">
            <div>
              <label class="block text-sm text-dark-400 mb-1">Источники RSS</label>
              <div class="space-y-2">
                <label v-for="source in newsSources" :key="source.id" class="flex items-center gap-2 text-sm text-dark-300">
                  <input type="checkbox" v-model="form.config.sources" :value="source.id" class="rounded" />
                  {{ source.name }}
                </label>
              </div>
            </div>
            <label class="flex items-center gap-2">
              <input type="checkbox" v-model="form.config.check_censorship" class="rounded" />
              <span class="text-sm text-dark-300">Проверять цензуру</span>
            </label>
            <label class="flex items-center gap-2">
              <input type="checkbox" v-model="form.config.summarize" class="rounded" />
              <span class="text-sm text-dark-300">Суммаризировать</span>
            </label>
          </div>
        </div>

        <!-- City config -->
        <div v-else-if="selectedType.type === 'city'">
          <h4 class="font-medium text-dark-200 mb-3">Городские каналы</h4>
          <div class="space-y-3">
            <div>
              <label class="block text-sm text-dark-400 mb-1">Города</label>
              <div class="grid grid-cols-2 gap-2">
                <label v-for="city in cities" :key="city" class="flex items-center gap-2 text-sm text-dark-300">
                  <input type="checkbox" v-model="form.config.cities" :value="city" class="rounded" />
                  {{ city }}
                </label>
              </div>
            </div>
            <label class="flex items-center gap-2">
              <input type="checkbox" v-model="form.config.include_weather" class="rounded" />
              <span class="text-sm text-dark-300">Добавлять погоду</span>
            </label>
          </div>
        </div>

        <!-- Affiliate config -->
        <div v-else-if="selectedType.type === 'affiliate'">
          <h4 class="font-medium text-dark-200 mb-3">Реферальные товары</h4>
          <div class="space-y-3">
            <div>
              <label class="block text-sm text-dark-400 mb-1">Постов в день</label>
              <input type="number" v-model.number="form.config.posts_per_day" class="input" min="1" max="10" />
            </div>
            <label class="flex items-center gap-2">
              <input type="checkbox" v-model="form.config.native_style" class="rounded" />
              <span class="text-sm text-dark-300">Нативный стиль (без явной рекламы)</span>
            </label>
          </div>
        </div>

        <!-- Default config -->
        <div v-else>
          <h4 class="font-medium text-dark-200 mb-3">Общие настройки</h4>
          <div class="space-y-3">
            <div>
              <label class="block text-sm text-dark-400 mb-1">Расписание (cron)</label>
              <input type="text" v-model="form.schedule" class="input" placeholder="*/30 * * * *" />
            </div>
            <div>
              <label class="block text-sm text-dark-400 mb-1">Конфигурация (JSON)</label>
              <textarea v-model="form.configJson" class="input h-24 font-mono text-sm" placeholder='{"key": "value"}'></textarea>
            </div>
          </div>
        </div>

        <!-- Common settings -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <h4 class="font-medium text-dark-200">Привязанные каналы</h4>
            <button @click="showBindModal = true" class="text-sm text-primary-400 hover:text-primary-300">
              + Привязать канал
            </button>
          </div>
          
          <div v-if="bindings.length === 0" class="text-dark-400 text-sm mb-3 p-3 bg-dark-700/30 rounded-lg">
            Нет привязанных каналов
          </div>
          <div v-else class="space-y-2 mb-4">
            <div
              v-for="binding in bindings"
              :key="binding.id"
              class="flex items-center justify-between p-3 bg-dark-700/50 rounded-lg"
            >
              <div>
                <span class="text-dark-200">{{ binding.channel_name }}</span>
                <span class="text-dark-500 text-sm ml-2">{{ binding.schedule || 'default' }}</span>
              </div>
              <button @click="unbindChannel(binding.id)" class="text-dark-400 hover:text-red-400 text-sm">
                Отвязать
              </button>
            </div>
          </div>

          <div class="pt-4 border-t border-dark-700">
            <label class="flex items-center gap-2 mb-3">
              <input type="checkbox" v-model="form.is_active" class="rounded" />
              <span class="text-sm text-dark-300">Тип контента активен</span>
            </label>
          </div>
        </div>
      </div>

      <div class="flex justify-end gap-3 mt-6 pt-6 border-t border-dark-700">
        <button @click="closeEditor" class="btn btn-secondary">Отмена</button>
        <button @click="saveContentType" class="btn btn-primary" :disabled="saving">
          {{ saving ? 'Сохранение...' : 'Сохранить' }}
        </button>
      </div>
    </div>

    <!-- Bind Channel Modal -->
    <div v-if="showBindModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showBindModal = false">
      <div class="bg-dark-800 rounded-xl p-6 w-full max-w-md border border-dark-700">
        <h2 class="text-xl font-bold text-dark-100 mb-4">Привязать канал</h2>

        <div class="space-y-4">
          <div>
            <label class="block text-sm text-dark-400 mb-1">Канал</label>
            <select v-model="bindForm.channel_id" class="input">
              <option :value="null" disabled>Выберите канал</option>
              <option v-for="channel in availableChannels" :key="channel.id" :value="channel.id">
                {{ channel.name }} ({{ getPlatformLabel(channel.platform) }})
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-dark-400 mb-1">Расписание (cron, опционально)</label>
            <input type="text" v-model="bindForm.schedule" class="input" placeholder="*/30 * * * *" />
          </div>
        </div>

        <div class="flex gap-3 mt-6">
          <button @click="showBindModal = false" class="btn btn-secondary flex-1">Отмена</button>
          <button @click="bindChannel" class="btn btn-primary flex-1" :disabled="bindLoading || !bindForm.channel_id">
            {{ bindLoading ? 'Привязка...' : 'Привязать' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toast.show" 
         class="fixed bottom-6 right-6 p-4 rounded-lg shadow-lg z-50"
         :class="toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'">
      <p class="text-white">{{ toast.message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, reactive, computed, watch } from 'vue'
import api from '@/api'
import {
  XMarkIcon,
  GlobeAltIcon,
  SparklesIcon,
  NewspaperIcon,
  BuildingOfficeIcon,
  ShoppingCartIcon,
  HeartIcon,
  CogIcon,
} from '@heroicons/vue/24/outline'

const contentTypes = ref<any[]>([])
const selectedType = ref<any>(null)
const bindings = ref<any[]>([])
const channels = ref<any[]>([])
const saving = ref(false)
const bindLoading = ref(false)
const showBindModal = ref(false)

const toast = reactive({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error',
})

const form = reactive({
  is_active: true,
  schedule: '',
  config: {} as Record<string, any>,
  configJson: '',
})

const bindForm = reactive({
  channel_id: null as number | null,
  schedule: '',
})

const zodiacSigns = ['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева', 'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы']
const cities = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань', 'Нижний Новгород', 'Челябинск', 'Самара']
const newsSources = [
  { id: 'tass', name: 'ТАСС' },
  { id: 'ria', name: 'РИА Новости' },
  { id: 'interfax', name: 'Интерфакс' },
  { id: 'rbc', name: 'РБК' },
]

const availableChannels = computed(() => {
  const boundIds = bindings.value.map(b => b.channel_id)
  return channels.value.filter(c => !boundIds.includes(c.id))
})

onMounted(async () => {
  await Promise.all([
    fetchContentTypes(),
    fetchChannels(),
  ])
})

async function fetchContentTypes() {
  try {
    const response = await api.get('/content-types')
    contentTypes.value = response.data
  } catch (error) {
    console.error('Failed to fetch content types')
    contentTypes.value = []
  }
}

async function fetchChannels() {
  try {
    const response = await api.get('/channels')
    channels.value = response.data
  } catch (error) {
    console.error('Failed to fetch channels')
  }
}

async function fetchBindings(contentTypeId: number) {
  try {
    const response = await api.get(`/content-types/${contentTypeId}/channels`)
    bindings.value = response.data
  } catch (error) {
    bindings.value = []
  }
}

function selectType(type: any) {
  selectedType.value = type
  form.is_active = type.is_active
  form.schedule = type.schedule || ''
  
  const config = type.config || {}
  form.config = { ...config }
  form.configJson = Object.keys(config).length > 0 ? JSON.stringify(config, null, 2) : ''
  
  if (type.type === 'horoscope' && !form.config.zodiac_signs) {
    form.config.zodiac_signs = [...zodiacSigns]
  }
  if (type.type === 'news' && !form.config.sources) {
    form.config.sources = ['tass', 'ria', 'interfax']
  }
  if (type.type === 'city' && !form.config.cities) {
    form.config.cities = ['Москва', 'Санкт-Петербург']
  }
  
  fetchBindings(type.id)
}

function closeEditor() {
  selectedType.value = null
  bindings.value = []
}

function showToast(message: string, type: 'success' | 'error' = 'success') {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => { toast.show = false }, 3000)
}

async function saveContentType() {
  if (!selectedType.value) return
  
  saving.value = true
  try {
    const data: any = {
      is_active: form.is_active,
      config: { ...form.config },
    }
    
    await api.patch(`/content-types/${selectedType.value.id}`, data)
    
    const index = contentTypes.value.findIndex(t => t.id === selectedType.value.id)
    if (index !== -1) {
      contentTypes.value[index] = { ...contentTypes.value[index], ...data }
    }
    
    showToast('Настройки сохранены', 'success')
  } catch (error) {
    showToast('Ошибка сохранения', 'error')
  } finally {
    saving.value = false
  }
}

async function bindChannel() {
  if (!selectedType.value || !bindForm.channel_id) return
  
  bindLoading.value = true
  try {
    const response = await api.post(`/content-types/${selectedType.value.id}/channels`, {
      channel_id: bindForm.channel_id,
      schedule: bindForm.schedule || null,
    })
    
    bindings.value.push(response.data)
    showBindModal.value = false
    bindForm.channel_id = null
    bindForm.schedule = ''
    showToast('Канал привязан', 'success')
  } catch (error) {
    showToast('Ошибка привязки', 'error')
  } finally {
    bindLoading.value = false
  }
}

async function unbindChannel(bindingId: number) {
  if (!selectedType.value || !confirm('Отвязать канал?')) return
  
  try {
    await api.delete(`/content-types/${selectedType.value.id}/channels/${bindingId}`)
    bindings.value = bindings.value.filter(b => b.id !== bindingId)
    showToast('Канал отвязан', 'success')
  } catch (error) {
    showToast('Ошибка отвязки', 'error')
  }
}

function getTypeIcon(type: string) {
  const icons: Record<string, any> = {
    reddit: GlobeAltIcon,
    horoscope: SparklesIcon,
    animal_facts: HeartIcon,
    news: NewspaperIcon,
    city: BuildingOfficeIcon,
    affiliate: ShoppingCartIcon,
    custom: CogIcon,
  }
  return icons[type] || CogIcon
}

function getTypeColor(type: string): string {
  const colors: Record<string, string> = {
    reddit: 'bg-orange-500',
    horoscope: 'bg-purple-500',
    animal_facts: 'bg-pink-500',
    news: 'bg-blue-500',
    city: 'bg-teal-500',
    affiliate: 'bg-green-500',
    custom: 'bg-gray-500',
  }
  return colors[type] || 'bg-dark-600'
}

function getTypeDescription(type: string): string {
  const descriptions: Record<string, string> = {
    reddit: 'Контент с Reddit',
    horoscope: 'Ежедневные гороскопы',
    animal_facts: 'Факты о животных',
    news: 'Новостной контент',
    city: 'Городские каналы',
    affiliate: 'Реферальные товары',
    custom: 'Кастомный контент',
  }
  return descriptions[type] || ''
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
