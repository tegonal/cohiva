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

<script setup>
import { onMounted, ref } from 'vue'

import { settings } from '../../config/settings.js'

let deferredPrompt
let bannerHasBeenShown = false

const showAppInstallBanner = ref(false)

function installApp() {
  showAppInstallBanner.value = false
  deferredPrompt.prompt()
  // Wait for the user to respond to the prompt
  deferredPrompt.userChoice.then((choiceResult) => {
    if (choiceResult.outcome === 'accepted') {
      console.log('User accepted the install prompt')
      neverShowAppInstallBanner()
    } else {
      console.log('User dismissed the install prompt')
    }
  })
}

function neverShowAppInstallBanner() {
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
      if (bannerHasBeenShown === true) return
      // Prevent the mini-infobar from appearing on mobile
      e.preventDefault()
      // Stash the event so it can be triggered later.
      deferredPrompt = e
      bannerHasBeenShown = true
      // Update UI notify the user they can install the PWA
      setTimeout(() => {
        showAppInstallBanner.value = true
      }, 3000)
    })
  }
})
</script>
