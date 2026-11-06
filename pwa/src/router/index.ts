import { defineRouter } from '#q-app'
import {
  createMemoryHistory,
  createRouter,
  createWebHistory,
  RouteLocationNormalized,
} from 'vue-router'

import { useAuthStore } from '@/stores/auth-store'

import routes from './routes'

export default defineRouter(function () {
  const createHistory = import.meta.env.QUASAR_SERVER
    ? createMemoryHistory
    : createWebHistory

  const Router = createRouter({
    history: createHistory('/'),
    routes,
    scrollBehavior: () => ({ left: 0, top: 0 }),
  })

  Router.beforeEach(async (to: RouteLocationNormalized) => {
    const publicPages = ['/login', '/auth/callback', '/auth/silent-renew']
    const authRequired = !publicPages.includes(to.path)
    const authStore = useAuthStore()

    if (!authStore.user && authStore.loading === false) {
      await authStore.initAuth()
    }

    if (authRequired) {
      const isAuthenticated = await authStore.checkAuth()

      if (!isAuthenticated) {
        authStore.setReturnUrl(to.fullPath)
        return '/login'
      }
    }

    // Allow navigation to proceed
    return true
  })

  Router.onError((error) => {
    console.error('Router navigation error:', error)
  })

  return Router
})
