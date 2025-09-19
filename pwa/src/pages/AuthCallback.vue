<template>
  <q-page class="flex flex-center">
    <div class="text-center">
      <q-spinner-dots color="primary" size="3em" />
      <p class="q-mt-md">
        {{ $t('auth.processing') || 'Anmeldung wird verarbeitet...' }}
      </p>
      <p v-if="error" class="text-negative q-mt-md">
        {{ error }}
      </p>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from 'stores/auth-store'

const authStore = useAuthStore()
const router = useRouter()
const error = ref<null | string>(null)

onMounted(async () => {
  try {
    // Handle the OAuth callback
    await authStore.handleCallback(router)
    // The store will handle the redirect
  } catch (err) {
    console.error('OAuth callback error:', err)
    const errorMessage = err instanceof Error ? err.message : String(err)
    error.value = errorMessage || 'Anmeldung fehlgeschlagen'

    // Redirect to login after a delay
    setTimeout(() => {
      router.push('/login')
    }, 3000)
  }
})
</script>
