import { defineBoot } from '#q-app/wrappers'

import { useAuthStore } from 'stores/auth-store'

export default defineBoot(() => {
  const authStore = useAuthStore()

  authStore.setupEventListeners()
  authStore.initAuth()
})
