<template>
  <q-layout view="hHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title> {{ settings.SITE_NICKNAME }} App </q-toolbar-title>

        <!-- <div>Quasar v{{ $q.version }}</div> -->
        <div>
          <img
            :alt="settings.SITE_NICKNAME + ' Logo'"
            src="/src/assets/logo.svg"
            style="width: 40px; height: 40px"
          />
        </div>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header> Links </q-item-label>

        <EssentialLink
          v-for="link in essentialLinks"
          :key="link.title"
          v-bind="link"
        />
        <q-item-label header> Einstellungen </q-item-label>
        <q-item>
          <q-item-section avatar>
            <q-icon name="info" />
          </q-item-section>

          <q-item-section>
            <q-item-label>App-Version</q-item-label>
            <q-item-label caption>{{ mainStore.appVersion }}</q-item-label>
          </q-item-section>
        </q-item>
        <q-item v-if="authStore.user">
          <q-item-section avatar>
            <q-icon name="person" />
          </q-item-section>

          <q-item-section>
            <q-item-label>Angemeldet als</q-item-label>
            <q-item-label caption>{{ authStore.username || authStore.userEmail || 'Unbekannt' }}</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable @click="settings_logout()" v-if="authStore.user">
          <q-item-section avatar>
            <q-icon name="logout" />
          </q-item-section>

          <q-item-section>
            <q-item-label>Abmelden</q-item-label>
            <q-item-label caption></q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-footer class="bg-white">
      <AppInstallBanner></AppInstallBanner>
      <AppUpdateBanner></AppUpdateBanner>
    </q-footer>

    <q-page-container>
      <router-view />
    </q-page-container>

    <!--
    <q-footer>
      <q-tabs v-model="tab">
        <router-link to="/reservation">
          <q-tab name="reservation" label="Reservation" icon="edit_calendar" />
        </router-link>
        <router-link to="/">
          <q-tab name="videos" label="Kalender" icon="calendar_month" />
        </router-link>
      </q-tabs>
    </q-footer> -->
  </q-layout>
</template>

<script setup lang="ts">
import { settings } from 'app/config/settings'
import { onBeforeUnmount, onMounted, ref } from 'vue'

import AppInstallBanner from 'components/AppInstallBanner.vue'
import AppUpdateBanner from 'components/AppUpdateBanner.vue'
import EssentialLink from 'components/EssentialLink.vue'
import { useAuthStore } from 'stores/auth-store'
import { useMainStore } from 'stores/main-store'

// Store instances
const authStore = useAuthStore()
const mainStore = useMainStore()

// Reactive state
const leftDrawerOpen = ref(false)
const updateTimeout = ref<null | ReturnType<typeof setInterval>>(null)

// Static data
const essentialLinks = settings.NAVIGATION_LINKS

// Functions
function settings_logout(): void {
  toggleLeftDrawer()
  authStore.logout()
}

function toggleLeftDrawer(): void {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

/* For service worker updates */
function updateRegistration(): void {
  if (mainStore.registration && !mainStore.registration.waiting) {
    console.log('Updating service-worker...')
    mainStore.registration.update()
  }
}

// Lifecycle hooks
onMounted(() => {
  updateRegistration()
  // Set up periodic service worker updates every 30 minutes
  updateTimeout.value = setInterval(() => {
    updateRegistration()
  }, 1000 * 60 * 30)
})

onBeforeUnmount(() => {
  if (updateTimeout.value) {
    clearInterval(updateTimeout.value)
    updateTimeout.value = null
  }
})
</script>
