<template>
  <transition
    appear
    enter-active-class="animated bounceIn"
    leave-active-class="animated fadeOut"
  >
    <div
      v-if="mainStore.showAppUpdatedBanner"
      class="banner-container bg-primary"
    >
      <div class="constrain-banner">
        <q-banner
          name="update-banner"
          dense
          inline-actions
          class="bg-primary text-white"
        >
          <template v-slot:avatar>
            <q-avatar
              name="signal_wifi_off"
              color="primary"
              icon="system_update"
              font-size="22px"
            />
          </template>
          <b>Es ist ein Update der App verfügbar. Jetzt aktualisieren?</b>
          <template v-slot:action>
            <q-btn
              dense
              flat
              label="Ja"
              class="q-px-sm"
              @click="updateApp(true)"
            />
            <q-btn
              dense
              flat
              label="Nein"
              class="q-px-sm"
              @click="updateApp(false)"
            />
          </template>
        </q-banner>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import { useMainStore } from 'stores/main-store'

const mainStore = useMainStore()
const refreshing = ref(false)

// Initialize version check
mainStore.update_version()

function updateApp(yes: boolean): void {
  mainStore.showAppUpdatedBanner = false
  if (!yes || refreshing.value) {
    return
  }
  refreshing.value = true
  if (mainStore.registration && mainStore.registration.waiting) {
    mainStore.registration.waiting.postMessage({ type: 'SKIP_WAITING' })
  }
  window.location.reload()
}
</script>
