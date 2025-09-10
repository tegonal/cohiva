<template>
  <!-- Silent renew page - no UI needed -->
  <div></div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import { useAuthStore } from 'stores/auth-store'

const authStore = useAuthStore()

onMounted(async () => {
  try {
    // Handle the silent renew callback
    await authStore.handleSilentCallback()
  } catch (error) {
    console.error('Silent renew error:', error)
  }
})
</script>
