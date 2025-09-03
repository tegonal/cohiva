<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
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

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { defineComponent, ref } from 'vue'

import { settings } from '../../config/settings.js'

export default defineComponent({
  name: 'SubpageLayout',
})
</script>

<script setup>
defineProps({ subpageTitle: String })
</script>
