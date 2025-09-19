<template>
  <q-page>
    <div class="flex flex-center q-py-xl">
      <img
        :alt="settings.SITE_NICKNAME + ' Logo'"
        :src="logoPath"
        style="width: 200px; height: 200px"
      />
    </div>
    <div class="row flex-center q-ma-md">
      <q-btn stack to="/calendar" padding="lg" flat :class="buttonClass">
        <q-icon
          name="sym_o_calendar_month"
          size="3.5rem"
          style="font-variation-settings: 'wght' 300"
        />
        <div class="text-caption">{{ $t('indexPage.buttons.calendar') }}</div>
      </q-btn>
      <q-btn stack to="/reservation" padding="lg" flat :class="buttonClass">
        <q-icon
          name="sym_o_edit_calendar"
          size="3.5rem"
          style="font-variation-settings: 'wght' 300"
        />
        <div class="text-caption">
          {{ $t('indexPage.buttons.reservation') }}
        </div>
      </q-btn>
      <q-btn
        v-if="mainStore.capabilities.residentHo8"
        stack
        :href="settings.BUTTON_LINKS.CHAT.link"
        target="_blank"
        padding="lg"
        flat
        :class="buttonClass"
      >
        <q-icon
          name="sym_o_chat"
          size="3.5rem"
          style="font-variation-settings: 'wght' 300"
        />
        <div class="text-caption">{{ $t('indexPage.buttons.chat') }}</div>
      </q-btn>
      <q-btn
        v-if="mainStore.capabilities.residentHo8"
        stack
        to="/repair"
        padding="lg"
        flat
        :class="buttonClass"
      >
        <q-icon
          name="sym_o_construction"
          size="3.5rem"
          style="font-variation-settings: 'wght' 300"
        />
        <div class="text-caption">{{ $t('indexPage.buttons.repair') }}</div>
      </q-btn>
      <q-btn
        v-if="mainStore.capabilities.residentHo8"
        stack
        :href="settings.BUTTON_LINKS.CLOUD.link"
        target="_blank"
        padding="lg"
        flat
        :class="buttonClass"
      >
        <q-icon
          name="sym_o_cloud"
          size="3.5rem"
          style="font-variation-settings: 'wght' 300"
        />
        <div class="text-caption">{{ $t('indexPage.buttons.cloud') }}</div>
      </q-btn>
      <q-btn
        v-if="mainStore.capabilities.residentHo8"
        stack
        :href="settings.BUTTON_LINKS.HANDBUCH.link"
        target="_blank"
        padding="lg"
        flat
        :class="buttonClass"
      >
        <q-icon
          name="sym_o_menu_book"
          size="3.5rem"
          style="font-variation-settings: 'wght' 300"
        />
        <div class="text-caption">{{ $t('indexPage.buttons.manual') }}</div>
      </q-btn>
      <q-btn
        v-if="mainStore.capabilities.depot8"
        stack
        to="/credit_accounting"
        padding="lg"
        flat
        :class="buttonClass"
      >
        <q-icon
          name="sym_o_storefront"
          size="3.5rem"
          style="font-variation-settings: 'wght' 300"
        />
        <div class="text-caption">{{ $t('indexPage.buttons.depot8') }}</div>
      </q-btn>
    </div>
    <div
      v-if="apiError"
      class="q-mt-md text-subtitle-1 text-negative text-center full-width"
    >
      <div>
        <q-icon name="warning" size="2em" />
      </div>
      <div>{{ apiError }}</div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from 'boot/axios'
import { useThemedLogo } from 'src/composables/use-themed-logo'
import { useAuthStore } from 'stores/auth-store'
import { useMainStore } from 'stores/main-store'

import { settings } from '../../config/settings'

const buttonClass = 'col-xs-6 col-sm-4 col-md-3 q-pa-md'

const apiError = ref('')

const { t } = useI18n()
const mainStore = useMainStore()
const authStore = useAuthStore()

// Theme-aware logo
const { logoPath } = useThemedLogo()

function getCapabilities() {
  // Get Caps from server and update mainStore.capabilities
  api
    .get('/api/v1/geno/capabilities/', {
      params: { appVersion: mainStore.appVersion },
    })
    .then((response) => {
      apiError.value = ''
      if (response.data.status == 'OK') {
        if (
          response.data.capabilities.credit_accounting_vendors.includes(
            'Depot8'
          )
        ) {
          mainStore.capabilities.depot8 = true
        }
        // TODO: Select other capabilities
        mainStore.capabilities.residentHo8 = true
      }
    })
    .catch((error) => {
      apiError.value = t('indexPage.errors.general')
      if ('response' in error) {
        if (
          error.response.data.detail ==
            t('indexPage.errors.missingCredentials') ||
          error.response.data.detail == t('indexPage.errors.invalidToken')
        ) {
          authStore.logout()
        }
      }
    })
}

onMounted(() => {
  getCapabilities()
})
</script>
