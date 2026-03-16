<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-dark-100">Цензура</h1>
        <p class="text-dark-400 mt-1">Правила фильтрации контента для РФ</p>
      </div>
      <button @click="showAddModal = true" class="btn btn-primary">
        + Добавить правило
      </button>
    </div>

    <!-- Quick stats -->
    <div class="grid grid-cols-3 gap-4 mb-8">
      <div class="card">
        <p class="text-dark-400 text-sm">Запрещённых слов</p>
        <p class="text-2xl font-bold text-red-400">{{ rules.filter(r => r.rule_type === 'banned').length }}</p>
      </div>
      <div class="card">
        <p class="text-dark-400 text-sm">Предупреждений</p>
        <p class="text-2xl font-bold text-yellow-400">{{ rules.filter(r => r.rule_type === 'warn').length }}</p>
      </div>
      <div class="card">
        <p class="text-dark-400 text-sm">На проверку</p>
        <p class="text-2xl font-bold text-blue-400">{{ rules.filter(r => r.rule_type === 'review').length }}</p>
      </div>
    </div>

    <!-- Check text form -->
    <div class="card mb-8">
      <h3 class="font-semibold text-dark-100 mb-4">Проверить текст</h3>
      <textarea v-model="checkText" class="input h-32 mb-4" placeholder="Вставьте текст для проверки..."></textarea>
      <div class="flex items-center gap-4">
        <button @click="checkCensorship" class="btn btn-primary" :disabled="checking">
          {{ checking ? 'Проверка...' : 'Проверить' }}
        </button>
        <div v-if="checkResult" class="flex items-center gap-2">
          <span v-if="checkResult.passed" class="badge badge-success">Прошёл проверку</span>
          <span v-else class="badge badge-danger">
            {{ checkResult.action === 'reject' ? 'Запрещено' : 'Требует проверки' }}
          </span>
        </div>
      </div>
      <div v-if="checkResult?.matched_rules?.length" class="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
        <p class="text-red-400 text-sm font-medium mb-2">Найдены совпадения:</p>
        <ul class="text-sm text-dark-300">
          <li v-for="rule in checkResult.matched_rules" :key="rule.pattern">
            • "{{ rule.pattern }}" ({{ rule.type }})
          </li>
        </ul>
      </div>
    </div>

    <!-- Rules list -->
    <div class="card">
      <h3 class="font-semibold text-dark-100 mb-4">Правила</h3>
      
      <div v-if="loading" class="text-center py-8 text-dark-400">Загрузка...</div>
      
      <div v-else-if="rules.length === 0" class="text-center py-8 text-dark-400">
        Нет правил. Добавьте первое.
      </div>

      <div v-else class="space-y-2">
        <div
          v-for="rule in rules"
          :key="rule.id"
          class="flex items-center justify-between p-3 bg-dark-700/50 rounded-lg"
        >
          <div>
            <p class="text-dark-100">{{ rule.pattern }}</p>
            <p class="text-sm text-dark-400">
              {{ rule.category || 'Без категории' }} • {{ rule.pattern_type }}
            </p>
          </div>
          <div class="flex items-center gap-2">
            <span :class="getRuleTypeBadge(rule.rule_type)">
              {{ getRuleTypeLabel(rule.rule_type) }}
            </span>
            <button @click="deleteRule(rule.id)" class="text-dark-400 hover:text-red-400">
              <TrashIcon class="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add modal -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showAddModal = false">
      <div class="bg-dark-800 rounded-xl p-6 w-full max-w-md border border-dark-700">
        <h2 class="text-xl font-bold text-dark-100 mb-4">Новое правило</h2>

        <form @submit.prevent="addRule" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Паттерн</label>
            <input v-model="newRule.pattern" type="text" class="input" required placeholder="слово или regex" />
          </div>

          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Тип паттерна</label>
            <select v-model="newRule.pattern_type" class="input">
              <option value="word">Слово</option>
              <option value="regex">Regex</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Действие</label>
            <select v-model="newRule.rule_type" class="input">
              <option value="banned">Запретить</option>
              <option value="warn">Предупреждение</option>
              <option value="review">На проверку</option>
              <option value="auto_edit">Автозамена</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Категория</label>
            <input v-model="newRule.category" type="text" class="input" placeholder="например: политика" />
          </div>

          <div v-if="newRule.rule_type === 'auto_edit'">
            <label class="block text-sm font-medium text-dark-300 mb-1">Замена</label>
            <input v-model="newRule.replacement" type="text" class="input" placeholder="текст для замены" />
          </div>

          <div class="flex gap-3 pt-4">
            <button type="button" @click="showAddModal = false" class="btn btn-secondary flex-1">
              Отмена
            </button>
            <button type="submit" class="btn btn-primary flex-1" :disabled="saving">
              {{ saving ? 'Сохранение...' : 'Добавить' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, reactive } from 'vue'
import api from '@/api'
import { TrashIcon } from '@heroicons/vue/24/outline'

const loading = ref(true)
const saving = ref(false)
const checking = ref(false)
const showAddModal = ref(false)
const rules = ref<any[]>([])
const checkText = ref('')
const checkResult = ref<any>(null)

const newRule = reactive({
  pattern: '',
  pattern_type: 'word',
  rule_type: 'banned',
  category: '',
  replacement: '',
})

onMounted(async () => {
  await fetchRules()
})

async function fetchRules() {
  loading.value = true
  try {
    const response = await api.get('/censorship/rules')
    rules.value = response.data
  } finally {
    loading.value = false
  }
}

async function addRule() {
  saving.value = true
  try {
    await api.post('/censorship/rules', newRule)
    await fetchRules()
    showAddModal.value = false
    newRule.pattern = ''
    newRule.category = ''
    newRule.replacement = ''
  } finally {
    saving.value = false
  }
}

async function deleteRule(id: number) {
  if (!confirm('Удалить правило?')) return
  await api.delete(`/censorship/rules/${id}`)
  rules.value = rules.value.filter(r => r.id !== id)
}

async function checkCensorship() {
  if (!checkText.value.trim()) return
  
  checking.value = true
  try {
    const response = await api.post('/censorship/check', { text: checkText.value })
    checkResult.value = response.data
  } finally {
    checking.value = false
  }
}

function getRuleTypeBadge(type: string): string {
  const badges: Record<string, string> = {
    banned: 'badge badge-danger',
    warn: 'badge badge-warning',
    review: 'badge badge-info',
    auto_edit: 'badge badge-neutral',
  }
  return badges[type] || 'badge badge-neutral'
}

function getRuleTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    banned: 'Запрет',
    warn: 'Предупреждение',
    review: 'Проверка',
    auto_edit: 'Замена',
  }
  return labels[type] || type
}
</script>
