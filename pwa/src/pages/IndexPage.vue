<template>
  <q-page>
    <div class="flex flex-center">
      <img
        :alt="settings.SITE_NICKNAME + ' Logo'"
        src="/src/assets/logo.svg"
        style="width: 200px; height: 200px"
      />
    </div>
    <div class="row flex-center q-ma-sm">
      <q-btn
        icon="calendar_month"
        label="Kalender"
        stack
        to="/calendar"
        padding="md"
        :class="buttonClass"
      ></q-btn>
      <q-btn
        icon="edit_calendar"
        label="Reservation"
        stack
        to="/reservation"
        padding="md"
        :class="buttonClass"
      ></q-btn>
      <q-btn
        v-if="mainStore.capabilities.residentHo8"
        icon="chat"
        label="Chat"
        stack
        :href="settings.BUTTON_LINKS.CHAT.link"
        target="_blank"
        padding="md"
        :class="buttonClass"
      ></q-btn>
      <q-btn
        v-if="mainStore.capabilities.residentHo8"
        icon="construction"
        label="Reparaturmeldung"
        stack
        to="/repair"
        padding="md"
        :class="buttonClass"
      ></q-btn>
      <q-btn
        v-if="mainStore.capabilities.residentHo8"
        icon="cloud"
        label="Cloud"
        stack
        :href="settings.BUTTON_LINKS.CLOUD.link"
        target="_blank"
        padding="md"
        :class="buttonClass"
      ></q-btn>
      <q-btn
        v-if="mainStore.capabilities.residentHo8"
        icon="menu_book"
        label="Handbuch"
        stack
        :href="settings.BUTTON_LINKS.HANDBUCH.link"
        target="_blank"
        padding="md"
        :class="buttonClass"
      ></q-btn>
      <q-btn
        v-if="mainStore.capabilities.depot8"
        icon="storefront"
        label="Depot8"
        stack
        to="/credit_accounting"
        padding="md"
        :class="buttonClass"
      ></q-btn>
    </div>
    <div v-if="test_mode">
      <p class="text-red text-center">
        TESTMODUS - Änderungen werden lediglich an einen Testserver übermittelt.
      </p>
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

<!--<script>
import { defineComponent } from "vue";
export default defineComponent({
  name: "IndexPage",
});
</script>-->

<script setup>
import { api } from 'boot/axios'
import { useAuthStore, useMainStore } from 'stores'
import { onMounted, ref } from 'vue'

import { settings } from '../../config/settings.js'

const buttonClass = 'col-xs-6 col-sm-4 col-md-3 q-my-xs'
const test_mode = process.env.TEST_MODE

const apiError = ref('')

const mainStore = useMainStore()
const authStore = useAuthStore()

function getCapabilities() {
  // Get Caps from server and update mainStore.capabilities
  api
    .get('/api/v1/geno/capabilities/', {
      headers: {
        Authorization: 'Token ' + authStore.token,
      },
      params: { appVersion: mainStore.appVersion },
    })
    .then((response) => {
      apiError.value = ''
      //console.log(response.data);
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
      apiError.value = 'Es ist ein Fehler aufgetreten.'
      if ('response' in error) {
        console.log('ERROR: ' + error.response.data.detail)
        if (
          error.response.data.detail == 'Anmeldedaten fehlen.' ||
          error.response.data.detail == 'Ungültiges Token'
        ) {
          authStore.logout()
        }
      } else {
        console.log('ERROR: ' + error)
      }
    })
}

onMounted(() => {
  getCapabilities()
})
</script>
