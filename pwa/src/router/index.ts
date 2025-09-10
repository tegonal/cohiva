import { defineRouter } from '#q-app/wrappers'
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
  RouteLocationNormalized,
} from 'vue-router'

import { useAuthStore } from 'stores/auth-store'

import routes from './routes'

export default defineRouter(function () {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === 'history'
      ? createWebHistory
      : createWebHashHistory

  const Router = createRouter({
    history: createHistory(process.env.VUE_ROUTER_BASE),
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
        console.log('Router: Authentication required -> redirect to /login')
        return '/login'
      }
    }

    // Allow navigation to proceed
    return true
  })

  return Router
})
