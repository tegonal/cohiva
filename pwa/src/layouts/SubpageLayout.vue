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

        <q-toolbar-title> {{ $t(subpageTitleKey) }} </q-toolbar-title>

        <!-- Language Switcher -->
        <LanguageSwitcher />
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
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'SubpageLayout',
})
</script>

<script setup lang="ts">
import DevOverlay from 'components/DevOverlay.vue'
import LanguageSwitcher from 'components/LanguageSwitcher.vue'

defineProps({ subpageTitleKey: String })
</script>

<style lang="scss" scoped></style>
