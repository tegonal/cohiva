<template>
  <Transition name="slide">
    <div v-if="isDevelopment" class="dev-overlay">
      <div class="dev-badge">
        DEV
        <q-tooltip anchor="top middle" self="bottom middle" :offset="[0, 8]">
          Development mode active
        </q-tooltip>
      </div>
      <div v-if="tokenTimeLeft" class="dev-info">
        <q-icon name="access_time" size="xs" />
        {{ tokenTimeLeft }}
        <q-tooltip anchor="top middle" self="bottom middle" :offset="[0, 8]">
          Access token expires in {{ tokenTimeLeft }}
        </q-tooltip>
      </div>
      <div
        v-if="hasRefreshToken"
        class="dev-info dev-refresh"
        @click="handleRefreshClick"
      >
        <q-icon name="refresh" size="xs" :class="{ rotate: isRefreshing }" />
        <span :class="refreshTokenStatus.class">{{
          refreshTokenStatus.text
        }}</span>
        <q-tooltip anchor="top middle" self="bottom middle" :offset="[0, 8]">
          Refresh token is {{ refreshTokenStatus.text }}. Click to manually
          refresh tokens.
        </q-tooltip>
      </div>
      <div v-if="mainStore.debugText" class="dev-debug">
        {{ mainStore.debugText }}
        <q-tooltip anchor="top middle" self="bottom middle" :offset="[0, 8]">
          Debug message (auto-clears after 5s)
        </q-tooltip>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

import { useAuthStore } from 'stores/auth-store'
import { useMainStore } from 'stores/main-store'

const isDevelopment = process.env.NODE_ENV === 'development'
const authStore = useAuthStore()
const mainStore = useMainStore()

const tokenTimeLeft = ref('')
const hasRefreshToken = ref(false)
const refreshTokenStatus = ref({ class: '', text: '' })
const isRefreshing = ref(false)

let updateInterval: null | ReturnType<typeof setInterval> = null

function formatTimeLeft(seconds: number): string {
  if (seconds <= 0) return 'expired'
  if (seconds < 60) return `${seconds}s`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m`
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  return `${hours}h${remainingMinutes > 0 ? remainingMinutes + 'm' : ''}`
}

async function handleRefreshClick() {
  if (isRefreshing.value) return

  isRefreshing.value = true
  mainStore.setDebugText('Refreshing...')

  try {
    await authStore.refreshToken()
    mainStore.setDebugText('Refreshed!')
    updateTokenTimers() // Update immediately after refresh
  } catch (error) {
    mainStore.setDebugText('Refresh failed')
    console.error('Token refresh failed:', error)
  } finally {
    isRefreshing.value = false
  }
}

function updateTokenTimers() {
  if (authStore.user) {
    // Access token time left
    if (authStore.user.expires_at) {
      const expiresAt = authStore.user.expires_at * 1000 // Convert to milliseconds
      const now = Date.now()
      const secondsLeft = Math.floor((expiresAt - now) / 1000)
      tokenTimeLeft.value = formatTimeLeft(secondsLeft)
    } else {
      tokenTimeLeft.value = ''
    }

    // Refresh token indicator
    // oidc-client-ts includes refresh_token but not its expiration time
    if (authStore.user.refresh_token) {
      hasRefreshToken.value = true
      // Since we don't have the refresh token expiration, show a simple status
      if (isRefreshing.value) {
        refreshTokenStatus.value = {
          class: 'refresh-active',
          text: 'refreshing',
        }
      } else {
        refreshTokenStatus.value = {
          class: 'refresh-active',
          text: 'active',
        }
      }
    } else {
      hasRefreshToken.value = false
      refreshTokenStatus.value = { class: '', text: '' }
    }
  } else {
    tokenTimeLeft.value = ''
    hasRefreshToken.value = false
    refreshTokenStatus.value = { class: '', text: '' }
  }
}

onMounted(() => {
  if (isDevelopment) {
    updateTokenTimers()
    // Update every 10 seconds
    updateInterval = setInterval(updateTokenTimers, 10000)
  }
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
    updateInterval = null
  }
})
</script>

<style lang="scss" scoped>
.dev-overlay {
  position: fixed;
  bottom: 4px;
  left: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.85);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-family: monospace;
  z-index: 9999;
  backdrop-filter: blur(8px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  user-select: none;

  .dev-badge {
    background: #ff4444;
    color: white;
    padding: 2px 6px;
    border-radius: 10px;
    font-weight: bold;
    font-size: 10px;
    pointer-events: none;
  }

  .dev-info {
    display: flex;
    align-items: center;
    gap: 3px;
    color: #4fc3f7;
    pointer-events: none;

    .q-icon {
      opacity: 0.7;
    }

    .refresh-active {
      color: #66bb6a;
    }
  }

  .dev-refresh {
    cursor: pointer;
    pointer-events: auto;
    padding: 2px 4px;
    border-radius: 8px;
    transition: background 0.2s;

    &:hover {
      background: rgba(255, 255, 255, 0.1);
    }

    &:active {
      background: rgba(255, 255, 255, 0.2);
    }

    .rotate {
      animation: spin 1s linear infinite;
    }
  }

  .dev-debug {
    color: #ffd54f;
    font-weight: 600;
    padding: 2px 6px;
    background: rgba(255, 213, 79, 0.15);
    border-radius: 10px;
  }
}

.slide-enter-active,
.slide-leave-active {
  transition:
    transform 0.3s ease,
    opacity 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
  opacity: 0;
}

.slide-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
