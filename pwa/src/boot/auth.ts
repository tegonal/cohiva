import { defineBoot } from '#q-app'

import { useAuthStore } from '@/stores/auth-store'

export default defineBoot(() => {
  const authStore = useAuthStore()

  authStore.setupEventListeners()
  authStore.initAuth()
})
