import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'
import type { Channel } from '@/api/types'

export const useChannelsStore = defineStore('channels', () => {
  const channels = ref<Channel[]>([])
  const currentChannel = ref<Channel | null>(null)
  const loading = ref(false)

  async function fetchChannels() {
    loading.value = true
    try {
      const response = await api.get('/channels')
      channels.value = response.data
    } finally {
      loading.value = false
    }
  }

  async function fetchChannel(id: number) {
    loading.value = true
    try {
      const response = await api.get(`/channels/${id}`)
      currentChannel.value = response.data
      return response.data
    } finally {
      loading.value = false
    }
  }

  async function createChannel(data: Partial<Channel>) {
    const response = await api.post('/channels', data)
    channels.value.push(response.data)
    return response.data
  }

  async function updateChannel(id: number, data: Partial<Channel>) {
    const response = await api.patch(`/channels/${id}`, data)
    const index = channels.value.findIndex(c => c.id === id)
    if (index !== -1) {
      channels.value[index] = response.data
    }
    return response.data
  }

  async function deleteChannel(id: number) {
    await api.delete(`/channels/${id}`)
    channels.value = channels.value.filter(c => c.id !== id)
  }

  return {
    channels,
    currentChannel,
    loading,
    fetchChannels,
    fetchChannel,
    createChannel,
    updateChannel,
    deleteChannel,
  }
})
