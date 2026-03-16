<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-dark-100">Реферальные товары</h1>
        <p class="text-dark-400 mt-1">Товары для продвижения в каналах</p>
      </div>
      <button @click="showAddModal = true" class="btn btn-primary">
        + Добавить товар
      </button>
    </div>

    <div v-if="loading" class="text-center py-12 text-dark-400">Загрузка...</div>

    <div v-else-if="products.length === 0" class="text-center py-12">
      <div class="text-dark-400 mb-4">Нет товаров</div>
      <button @click="showAddModal = true" class="btn btn-primary">
        Добавить первый товар
      </button>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="product in products"
        :key="product.id"
        class="card hover:border-dark-600 transition-colors"
      >
        <div class="flex items-start gap-4">
          <div v-if="product.image_url" class="w-16 h-16 rounded-lg overflow-hidden bg-dark-700 flex-shrink-0">
            <img :src="product.image_url" class="w-full h-full object-cover" />
          </div>
          <div v-else class="w-16 h-16 rounded-lg bg-dark-700 flex items-center justify-center flex-shrink-0">
            <ShoppingBagIcon class="w-8 h-8 text-dark-500" />
          </div>
          
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-dark-100 truncate">{{ product.name }}</h3>
            <p class="text-sm text-dark-400 truncate">{{ product.category || 'Без категории' }}</p>
            <p v-if="product.price" class="text-sm text-accent-400">{{ product.price }}</p>
          </div>
        </div>
        
        <p class="text-dark-300 text-sm mt-3 line-clamp-2">{{ product.description }}</p>
        
        <div class="flex items-center justify-between mt-4 pt-4 border-t border-dark-700">
          <span :class="product.is_active ? 'badge badge-success' : 'badge badge-neutral'">
            {{ product.is_active ? 'Активен' : 'Отключен' }}
          </span>
          <div class="flex gap-2">
            <button @click="editProduct(product)" class="text-dark-400 hover:text-dark-100 text-sm">
              Изменить
            </button>
            <button @click="deleteProduct(product.id)" class="text-dark-400 hover:text-red-400 text-sm">
              Удалить
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit modal -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" @click.self="closeModal">
      <div class="bg-dark-800 rounded-xl p-6 w-full max-w-lg border border-dark-700 max-h-[90vh] overflow-y-auto">
        <h2 class="text-xl font-bold text-dark-100 mb-4">
          {{ editingProduct ? 'Редактировать товар' : 'Новый товар' }}
        </h2>

        <form @submit.prevent="saveProduct" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Название *</label>
            <input v-model="form.name" type="text" class="input" required />
          </div>

          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Категория</label>
            <input v-model="form.category" type="text" class="input" placeholder="Здоровье, Красота..." />
          </div>

          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Реферальная ссылка *</label>
            <input v-model="form.ref_url" type="url" class="input" required placeholder="https://..." />
          </div>

          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Описание</label>
            <textarea v-model="form.description" class="input h-24"></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Ключевые слова (через запятую)</label>
            <input v-model="form.keywordsText" type="text" class="input" placeholder="здоровье, витамины" />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-dark-300 mb-1">Цена</label>
              <input v-model="form.price" type="text" class="input" placeholder="1990 ₽" />
            </div>
            <div>
              <label class="block text-sm font-medium text-dark-300 mb-1">URL изображения</label>
              <input v-model="form.image_url" type="url" class="input" placeholder="https://..." />
            </div>
          </div>

          <div class="flex items-center gap-2">
            <input v-model="form.is_active" type="checkbox" id="product_active" class="rounded" />
            <label for="product_active" class="text-sm text-dark-300">Активен</label>
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
import api from '@/api'
import { ShoppingBagIcon } from '@heroicons/vue/24/outline'

const loading = ref(true)
const saving = ref(false)
const showAddModal = ref(false)
const products = ref<any[]>([])
const editingProduct = ref<any>(null)

const form = reactive({
  name: '',
  category: '',
  ref_url: '',
  description: '',
  keywordsText: '',
  price: '',
  image_url: '',
  is_active: true,
})

onMounted(async () => {
  await fetchProducts()
})

async function fetchProducts() {
  loading.value = true
  try {
    const response = await api.get('/products')
    products.value = response.data
  } finally {
    loading.value = false
  }
}

function editProduct(product: any) {
  editingProduct.value = product
  form.name = product.name
  form.category = product.category || ''
  form.ref_url = product.ref_url
  form.description = product.description || ''
  form.keywordsText = product.keywords?.join(', ') || ''
  form.price = product.price || ''
  form.image_url = product.image_url || ''
  form.is_active = product.is_active
  showAddModal.value = true
}

function closeModal() {
  showAddModal.value = false
  editingProduct.value = null
  form.name = ''
  form.category = ''
  form.ref_url = ''
  form.description = ''
  form.keywordsText = ''
  form.price = ''
  form.image_url = ''
  form.is_active = true
}

async function saveProduct() {
  saving.value = true
  
  try {
    const data: any = {
      name: form.name,
      category: form.category || null,
      ref_url: form.ref_url,
      description: form.description || null,
      keywords: form.keywordsText ? form.keywordsText.split(',').map(k => k.trim()) : null,
      price: form.price || null,
      image_url: form.image_url || null,
      is_active: form.is_active,
    }
    
    if (editingProduct.value) {
      await api.patch(`/products/${editingProduct.value.id}`, data)
    } else {
      await api.post('/products', data)
    }
    
    await fetchProducts()
    closeModal()
  } catch (error) {
    alert('Ошибка сохранения')
  } finally {
    saving.value = false
  }
}

async function deleteProduct(id: number) {
  if (!confirm('Удалить товар?')) return
  await api.delete(`/products/${id}`)
  products.value = products.value.filter(p => p.id !== id)
}
</script>
