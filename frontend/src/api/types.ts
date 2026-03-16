export interface Channel {
  id: number
  name: string
  slug: string
  platform: 'telegram' | 'vk' | 'wordpress'
  config: Record<string, any> | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ContentType {
  id: number
  name: string
  type: 'reddit' | 'horoscope' | 'animal_facts' | 'news' | 'city' | 'affiliate' | 'custom'
  description: string | null
  config: Record<string, any> | null
  is_active: boolean
  created_at: string
}

export interface Post {
  id: number
  channel_id: number
  content_type_id: number | null
  status: 'draft' | 'pending' | 'approved' | 'scheduled' | 'published' | 'failed' | 'rejected'
  title: string | null
  body: string
  media_urls: string[] | null
  source_url: string | null
  source_title: string | null
  censorship_flags: Record<string, any> | null
  censorship_passed: boolean
  ai_metadata: Record<string, any> | null
  generated_at: string | null
  scheduled_at: string | null
  published_at: string | null
  created_at: string
  updated_at: string
}

export interface PublishQueueItem {
  id: number
  post_id: number
  platform: 'telegram' | 'vk' | 'wordpress'
  scheduled_at: string
  priority: number
  attempts: number
  max_attempts: number
  status: string
  error_message: string | null
  created_at: string
}

export interface User {
  id: number
  username: string
  is_active: boolean
  created_at: string
}
