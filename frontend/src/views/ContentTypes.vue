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
        <button @click="selectedType = null" class="text-dark-400 hover:text-dark-100">
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Reddit config -->
        <div v-if="selectedType.type === 'reddit'">
          <h4 class="font-medium text-dark-200 mb-3">Настройки Reddit</h4>
          <div class="space-y-3">
            <div>
              <label class="block text-sm text-dark-400 mb-1">Subreddits</label>
              <textarea class="input h-24" placeholder="interestingasfuck&#10;todayilearned&#10;mildlyinteresting"></textarea>
            </div>
            <div>
              <label class="block text-sm text-dark-400 mb-1">Мин. рейтинг</label>
              <input type="number" class="input" value="1000" />
            </div>
            <div class="flex items-center gap-4">
              <label class="flex items-center gap-2">
                <input type="checkbox" checked class="rounded" />
                <span class="text-sm text-dark-300">Переводить</span>
              </label>
              <label class="flex items-center gap-2">
                <input type="checkbox" checked class="rounded" />
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
              <input type="time" class="input" value="00:05" />
            </div>
            <div>
              <label class="block text-sm text-dark-400 mb-1">Знаки зодиака</label>
              <div class="grid grid-cols-3 gap-2">
                <label v-for="sign in zodiacSigns" :key="sign" class="flex items-center gap-2 text-sm text-dark-300">
                  <input type="checkbox" checked class="rounded" />
                  {{ sign }}
                </label>
              </div>
            </div>
            <label class="flex items-center gap-2">
              <input type="checkbox" checked class="rounded" />
              <span class="text-sm text-dark-300">Использовать AI генерацию</span>
            </label>
          </div>
        </div>

        <!-- News config -->
        <div v-else-if="selectedType.type === 'news'">
          <h4 class="font-medium text-dark-200 mb-3">Настройки новостей</h4>
          <div class="space-y-3">
            <div>
              <label class="block text-sm text-dark-400 mb-1">Источники</label>
              <div class="space-y-2">
                <label class="flex items-center gap-2 text-sm text-dark-300">
                  <input type="checkbox" checked class="rounded" />
                  ТАСС
                </label>
                <label class="flex items-center gap-2 text-sm text-dark-300">
                  <input type="checkbox" checked class="rounded" />
                  РИА Новости
                </label>
                <label class="flex items-center gap-2 text-sm text-dark-300">
                  <input type="checkbox" checked class="rounded" />
                  Интерфакс
                </label>
                <label class="flex items-center gap-2 text-sm text-dark-300">
                  <input type="checkbox" class="rounded" />
                  РБК
                </label>
              </div>
            </div>
            <label class="flex items-center gap-2">
              <input type="checkbox" checked class="rounded" />
              <span class="text-sm text-dark-300">Проверять цензуру</span>
            </label>
            <label class="flex items-center gap-2">
              <input type="checkbox" checked class="rounded" />
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
                  <input type="checkbox" :checked="['Москва', 'Санкт-Петербург'].includes(city)" class="rounded" />
                  {{ city }}
                </label>
              </div>
            </div>
            <label class="flex items-center gap-2">
              <input type="checkbox" checked class="rounded" />
              <span class="text-sm text-dark-300">Добавлять погоду</span>
            </label>
          </div>
        </div>

        <!-- Default -->
        <div v-else>
          <h4 class="font-medium text-dark-200 mb-3">Общие настройки</h4>
          <div class="space-y-3">
            <div>
              <label class="block text-sm text-dark-400 mb-1">Расписание</label>
              <input type="text" class="input" placeholder="*/30 * * * *" />
            </div>
            <div>
              <label class="block text-sm text-dark-400 mb-1">Конфигурация (JSON)</label>
              <textarea class="input h-24 font-mono text-sm" placeholder='{"key": "value"}'></textarea>
            </div>
          </div>
        </div>

        <!-- Channel bindings -->
        <div>
          <h4 class="font-medium text-dark-200 mb-3">Привязанные каналы</h4>
          <div v-if="bindings.length === 0" class="text-dark-400 text-sm mb-3">
            Нет привязанных каналов
          </div>
          <div v-else class="space-y-2 mb-4">
            <div
              v-for="binding in bindings"
              :key="binding.id"
              class="flex items-center justify-between p-2 bg-dark-700/50 rounded"
            >
              <span class="text-dark-200">{{ binding.channel_name }}</span>
              <button class="text-dark-400 hover:text-red-400 text-sm">Отвязать</button>
            </div>
          </div>
          
          <button class="btn btn-secondary w-full">
            + Привязать канал
          </button>
        </div>
      </div>

      <div class="flex justify-end gap-3 mt-6 pt-6 border-t border-dark-700">
        <button @click="selectedType = null" class="btn btn-secondary">Отмена</button>
        <button class="btn btn-primary">Сохранить</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
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

const zodiacSigns = ['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева', 'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы']
const cities = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань', 'Нижний Новгород', 'Челябинск', 'Самара']

onMounted(async () => {
  await fetchContentTypes()
})

async function fetchContentTypes() {
  try {
    const response = await api.get('/content-types')
    contentTypes.value = response.data
  } catch (error) {
    // Mock data
    contentTypes.value = [
      { id: 1, name: 'Reddit', type: 'reddit', is_active: true, description: 'Парсинг лучших постов с Reddit' },
      { id: 2, name: 'Гороскопы', type: 'horoscope', is_active: true, description: 'Ежедневные гороскопы для всех знаков' },
      { id: 3, name: 'Факты о животных', type: 'animal_facts', is_active: true, description: 'Интересные факты о животных' },
      { id: 4, name: 'Новости', type: 'news', is_active: true, description: 'Новости с цензурой для РФ' },
      { id: 5, name: 'Городские', type: 'city', is_active: false, description: 'Локальный контент для городов' },
      { id: 6, name: 'Реферальные товары', type: 'affiliate', is_active: true, description: 'Native-посты с товарами' },
    ]
  }
}

function selectType(type: any) {
  selectedType.value = type
  bindings.value = []
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
</script>
