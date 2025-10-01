<template>
  <q-layout view="hHh Lpr lFf">
    <q-header class="app-header">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title> {{ settings.siteNickname }} App </q-toolbar-title>

        <!-- Language Switcher -->
        <LanguageSwitcher />
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-scroll-area class="fit">
        <q-list>
          <q-item-label header>{{
            $t('mainLayout.navigation.links')
          }}</q-item-label>

          <EssentialLink
            v-for="link in essentialLinks"
            :key="link.title"
            v-bind="link"
          />
          <q-item-label header>{{
            $t('mainLayout.navigation.settings')
          }}</q-item-label>
          <q-item>
            <q-item-section avatar>
              <q-icon name="info" />
            </q-item-section>

            <q-item-section>
              <q-item-label>{{
                $t('mainLayout.appVersion.label')
              }}</q-item-label>
              <q-item-label caption>{{ mainStore.appVersion }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-item v-if="authStore.user">
            <q-item-section avatar>
              <q-icon name="person" />
            </q-item-section>

            <q-item-section>
              <q-item-label>{{
                $t('mainLayout.user.loggedInAs')
              }}</q-item-label>
              <q-item-label caption>{{
                authStore.username ||
                authStore.userEmail ||
                $t('mainLayout.user.unknown')
              }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-item clickable @click="settings_logout()" v-if="authStore.user">
            <q-item-section avatar>
              <q-icon name="logout" />
            </q-item-section>

            <q-item-section>
              <q-item-label>{{ $t('mainLayout.user.logout') }}</q-item-label>
              <q-item-label caption></q-item-label>
            </q-item-section>
          </q-item>

          <!-- Dev Mode PWA Install Button -->
          <q-item v-if="isDev" clickable @click="showPwaInstallDialog">
            <q-item-section avatar>
              <q-icon name="sym_o_install_mobile" />
            </q-item-section>

            <q-item-section>
              <q-item-label>{{
                $t('mainLayout.pwaInstall.label')
              }}</q-item-label>
              <q-item-label caption>{{
                $t('mainLayout.pwaInstall.devModeOnly')
              }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>

        <!-- Theme Toggle at the bottom -->
        <div class="absolute-bottom q-pa-md">
          <q-item-label header class="q-pb-sm">{{
            $t('mainLayout.theme.label', 'Design')
          }}</q-item-label>
          <ThemeModeToggle />
        </div>
      </q-scroll-area>
    </q-drawer>

    <q-footer class="bg-white">
      <AppUpdateBanner></AppUpdateBanner>
    </q-footer>

    <q-page-container>
      <router-view />
    </q-page-container>

    <!-- Development Overlay -->
    <DevOverlay />
  </q-layout>
  <pwa-install></pwa-install>
</template>

<script setup lang="ts">
import { settings } from 'app/tenant-config/settings'
import { onBeforeUnmount, onMounted, ref } from 'vue'

import AppUpdateBanner from 'components/AppUpdateBanner.vue'
import DevOverlay from 'components/DevOverlay.vue'
import EssentialLink from 'components/EssentialLink.vue'
import LanguageSwitcher from 'components/LanguageSwitcher.vue'
import ThemeModeToggle from 'components/ThemeModeToggle.vue'
import { useAuthStore } from 'stores/auth-store'
import { useMainStore } from 'stores/main-store'

// Check if we're in dev mode
const isDev = process.env.NODE_ENV === 'development'

// Store instances
const authStore = useAuthStore()
const mainStore = useMainStore()

// Reactive state
const leftDrawerOpen = ref(false)
const updateTimeout = ref<null | ReturnType<typeof setInterval>>(null)

// Static data
const essentialLinks = settings.navigationLinks

// Functions
function settings_logout(): void {
  toggleLeftDrawer()
  authStore.logout()
}

function showPwaInstallDialog(): void {
  const pwaInstall = document.querySelector('pwa-install') as any
  if (pwaInstall) {
    pwaInstall.showDialog(true)
  }
}

function toggleLeftDrawer(): void {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

/* For service worker updates */
function updateRegistration(): void {
  if (mainStore.registration && !mainStore.registration.waiting) {
    mainStore.registration.update()
  }
}

// Lifecycle hooks
onMounted(() => {
  updateRegistration()
  // Set up periodic service worker updates every 30 minutes
  updateTimeout.value = setInterval(
    () => {
      updateRegistration()
    },
    1000 * 60 * 30
  )
})

onBeforeUnmount(() => {
  if (updateTimeout.value) {
    clearInterval(updateTimeout.value)
    updateTimeout.value = null
  }
})
</script>

<style lang="scss" scoped></style>
