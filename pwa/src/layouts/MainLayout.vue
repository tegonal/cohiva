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
            <q-item-label caption>{{ authStore.user }}</q-item-label>
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

<script setup>
import AppInstallBanner from 'components/AppInstallBanner.vue'
import AppUpdateBanner from 'components/AppUpdateBanner.vue'
import EssentialLink from 'components/EssentialLink.vue'
import { useAuthStore, useMainStore } from 'stores'
import { onBeforeUnmount, onMounted, ref } from 'vue'

import { settings } from '../../config/settings.js'

const leftDrawerOpen = ref(false)
const authStore = useAuthStore()
const mainStore = useMainStore()

function settings_logout() {
  toggleLeftDrawer()
  authStore.logout()
}

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

const essentialLinks = settings.NAVIGATION_LINKS

/* For service worker updates */
function updateRegistration() {
  if (mainStore.registration && !mainStore.registration.waiting) {
    console.log('Updating service-worker...')
    mainStore.registration.update()
  }
}

let updateTimeout = setInterval(
  function () {
    updateRegistration()
  }.bind(this),
  1000 * 60 * 30
)

onMounted(() => updateRegistration())
onBeforeUnmount(() => {
  if (updateTimeout) {
    clearInterval(updateTimeout)
  }
})
</script>
