import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'
import type { Post } from '@/api/types'

export const usePostsStore = defineStore('posts', () => {
  const posts = ref<Post[]>([])
  const currentPost = ref<Post | null>(null)
  const loading = ref(false)

  async function fetchPosts(params: Record<string, any> = {}) {
    loading.value = true
    try {
      const response = await api.get('/posts', { params })
      posts.value = response.data
    } finally {
      loading.value = false
    }
  }

  async function fetchPost(id: number) {
    loading.value = true
    try {
      const response = await api.get(`/posts/${id}`)
      currentPost.value = response.data
      return response.data
    } finally {
      loading.value = false
    }
  }

  async function createPost(data: Partial<Post>) {
    const response = await api.post('/posts', data)
    posts.value.unshift(response.data)
    return response.data
  }

  async function updatePost(id: number, data: Partial<Post>) {
    const response = await api.patch(`/posts/${id}`, data)
    const index = posts.value.findIndex(p => p.id === id)
    if (index !== -1) {
      posts.value[index] = response.data
    }
    return response.data
  }

  async function deletePost(id: number) {
    await api.delete(`/posts/${id}`)
    posts.value = posts.value.filter(p => p.id !== id)
  }

  async function approvePost(id: number) {
    const response = await api.post(`/posts/${id}/approve`)
    const index = posts.value.findIndex(p => p.id === id)
    if (index !== -1) {
      posts.value[index] = response.data
    }
    return response.data
  }

  async function rejectPost(id: number) {
    const response = await api.post(`/posts/${id}/reject`)
    const index = posts.value.findIndex(p => p.id === id)
    if (index !== -1) {
      posts.value[index] = response.data
    }
    return response.data
  }

  return {
    posts,
    currentPost,
    loading,
    fetchPosts,
    fetchPost,
    createPost,
    updatePost,
    deletePost,
    approvePost,
    rejectPost,
  }
})
