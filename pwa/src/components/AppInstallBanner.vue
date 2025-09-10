<template>
  <transition
    appear
    enter-active-class="animated bounceIn"
    leave-active-class="animated fadeOut"
  >
    <div v-if="showAppInstallBanner" class="banner-container bg-primary">
      <div class="constrain-banner">
        <q-banner dense inline-actions class="bg-primary text-white">
          <template v-slot:avatar>
            <q-avatar
              name="signal_wifi_off"
              color="primary"
              icon="system_update"
              font-size="22px"
            />
          </template>
          <b>Möchtest du die {{ settings.SITE_NICKNAME }}-App installieren?</b>
          <template v-slot:action>
            <q-btn dense flat label="Ja" class="q-px-sm" @click="installApp" />
            <q-btn
              dense
              flat
              @click="showAppInstallBanner = false"
              label="Später"
              class="q-px-sm"
            />
            <q-btn
              dense
              flat
              label="Nie"
              class="q-px-sm"
              @click="neverShowAppInstallBanner"
            />
          </template>
        </q-banner>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { settings } from 'app/config/settings'
import { onMounted, ref } from 'vue'

// Type definition for the BeforeInstallPromptEvent
interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{
    outcome: 'accepted' | 'dismissed'
    platform: string
  }>
}

// Reactive state
const deferredPrompt = ref<BeforeInstallPromptEvent | null>(null)
const bannerHasBeenShown = ref(false)
const showAppInstallBanner = ref(false)

function installApp(): void {
  showAppInstallBanner.value = false
  if (deferredPrompt.value) {
    deferredPrompt.value.prompt()
    // Wait for the user to respond to the prompt
    deferredPrompt.value.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the install prompt')
        neverShowAppInstallBanner()
      } else {
        console.log('User dismissed the install prompt')
      }
    })
  }
}

function neverShowAppInstallBanner(): void {
  showAppInstallBanner.value = false
  localStorage.setItem('neverShowInstall', 'true')
}

onMounted(() => {
  const neverShowInstall = localStorage.getItem('neverShowInstall')
  console.log(`Mounted app-install-banner nevershow = ${neverShowInstall}`)
  if (neverShowInstall != 'true') {
    console.log('Added event listener')
    window.addEventListener('beforeinstallprompt', (e) => {
      console.log('Triggered beforeinstallprompt listener')
      if (bannerHasBeenShown.value) return
      // Prevent the mini-infobar from appearing on mobile
      e.preventDefault()
      // Stash the event so it can be triggered later.
      deferredPrompt.value = e as BeforeInstallPromptEvent
      bannerHasBeenShown.value = true
      // Update UI notify the user they can install the PWA
      setTimeout(() => {
        showAppInstallBanner.value = true
      }, 3000)
    })
  }
})
</script>
