<template>
  <q-layout view="lHh Lpr lFf">
    <q-header class="app-header">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="arrow_back"
          aria-label="Menu"
          @click="$router.back()"
        />

        <q-toolbar-title> {{ subpageTitle }} </q-toolbar-title>

        <!-- Language Switcher -->
        <LanguageSwitcher />

        <!-- <div>Quasar v{{ $q.version }}</div> -->
        <div class="toolbar-logo">
          <img
            :alt="settings.SITE_NICKNAME + ' Logo'"
            :src="logoPath"
          />
        </div>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>

    <!-- Development Overlay -->
    <DevOverlay />
  </q-layout>
</template>

<script lang="ts">
import { settings } from 'app/config/settings'
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'SubpageLayout',
})
</script>

<script setup lang="ts">
import DevOverlay from 'components/DevOverlay.vue'
import LanguageSwitcher from 'components/LanguageSwitcher.vue'
import { useThemedLogo } from 'src/composables/use-themed-logo'

// Theme-aware logo
const { logoPath } = useThemedLogo()

defineProps({ subpageTitle: String })
</script>

<style lang="scss" scoped>
.toolbar-logo {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;

  img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
}
</style>
