import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    component: () => import('@/components/layout/Layout.vue'),
    meta: { auth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
      },
      {
        path: 'channels',
        name: 'Channels',
        component: () => import('@/views/Channels.vue'),
      },
      {
        path: 'channels/:id',
        name: 'ChannelEdit',
        component: () => import('@/views/ChannelEdit.vue'),
      },
      {
        path: 'posts',
        name: 'Posts',
        component: () => import('@/views/Posts.vue'),
      },
      {
        path: 'posts/:id',
        name: 'PostEdit',
        component: () => import('@/views/PostEdit.vue'),
      },
      {
        path: 'queue',
        name: 'Queue',
        component: () => import('@/views/Queue.vue'),
      },
      {
        path: 'content',
        name: 'ContentTypes',
        component: () => import('@/views/ContentTypes.vue'),
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/Products.vue'),
      },
      {
        path: 'censorship',
        name: 'Censorship',
        component: () => import('@/views/Censorship.vue'),
      },
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('@/views/Analytics.vue'),
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.auth && !authStore.isAuthenticated) {
    next({ name: 'Login' })
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
