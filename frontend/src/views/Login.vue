<template>
  <div class="min-h-screen flex items-center justify-center bg-dark-900 px-4">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 mb-4">
          <span class="text-3xl font-bold text-white">A</span>
        </div>
        <h1 class="text-2xl font-bold text-dark-100">Autoposting</h1>
        <p class="text-dark-400 mt-2">Войдите в панель управления</p>
      </div>

      <form @submit.prevent="handleLogin" class="card">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Логин</label>
            <input
              v-model="username"
              type="text"
              class="input"
              placeholder="admin"
              required
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-1">Пароль</label>
            <input
              v-model="password"
              type="password"
              class="input"
              placeholder="••••••••"
              required
            />
          </div>

          <div v-if="error" class="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg p-3">
            {{ error }}
          </div>

          <button
            type="submit"
            class="btn btn-primary w-full"
            :disabled="loading"
          >
            <span v-if="loading">Входим...</span>
            <span v-else>Войти</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  
  const result = await authStore.login(username.value, password.value)
  
  if (result.success) {
    router.push('/')
  } else {
    error.value = result.error
  }
  
  loading.value = false
}
</script>
