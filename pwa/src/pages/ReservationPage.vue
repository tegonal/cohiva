<template>
  <q-page padding class="">
    <!-- <q-page class="flex flex-center">-->
    <h4 class="q-mx-xs q-my-md">Deine Reservationen</h4>

    <div class="" v-if="hasReservations">
      <q-list style="max-width: 400px">
        <div v-for="reservation in reservations" :key="reservation.id">
          <q-item>
            <q-item-section>
              <q-item-label>{{ reservation.title }}</q-item-label>
              <q-item-label caption lines="1" v-if="reservation.summary">{{
                reservation.summary
              }}</q-item-label>
              <q-item-label
                caption
                lines="1"
                :class="reservation.cancelled ? 'text-strike ' : ''"
                >{{ reservation.date }}</q-item-label
              >
              <q-item-label
                caption
                lines="1"
                v-if="reservation.cancelled"
                class="text-negative"
              >
                STORNIERT
              </q-item-label>
            </q-item-section>

            <q-item-section side top>
              <!-- <q-item-label caption>5 min ago</q-item-label>
            <q-icon name="star" color="yellow" /> -->
              <q-btn
                icon="edit"
                name="Editieren"
                v-if="reservation.canEdit"
                @click="editReservation(reservation)"
              />
            </q-item-section>
          </q-item>
          <q-separator spaced inset />
        </div>
      </q-list>
    </div>
    <div class="q-ma-xs" v-else>
      Du hast keine bevorstehenden Reservationen. Erstelle eine neue Reservation
      mit dem Plus-Knopf unten rechts.
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

    <div v-if="hasPastReservations">
      <h6 class="q-mx-xs q-my-md text-grey-6" v-if="hasPastReservations">
        Vergangene Reservationen
      </h6>
      <q-list style="max-width: 400px">
        <div v-for="reservation in past_reservations" :key="reservation.id">
          <q-item>
            <q-item-section>
              <q-item-label>{{ reservation.title }}</q-item-label>
              <q-item-label caption lines="1" v-if="reservation.summary">{{
                reservation.summary
              }}</q-item-label>
              <q-item-label caption lines="1">{{
                reservation.date
              }}</q-item-label>
            </q-item-section>

            <q-item-section side top>
              <!-- <q-item-label caption>5 min ago</q-item-label>
            <q-icon name="star" color="yellow" /> -->
              <q-btn icon="edit" name="Editieren" v-if="reservation.canEdit" />
            </q-item-section>
          </q-item>
          <q-separator spaced inset />
        </div>
      </q-list>
    </div>

    <q-dialog v-model="confirmCancelation" persistent>
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="question_mark" color="primary" text-color="white" />
          <span class="q-ml-sm text-h6"> Reservation löschen?</span>
        </q-card-section>
        <q-card-section class="row items-center">
          <p>
            Reservationen können momentan noch nicht geändert, sondern nur
            storniert werden. Danach kannst du eine neue Reservation erfassen.
          </p>
          <p class="q-mb-sx">
            <b>Möchtest du die folgende Reservation definitiv stornieren?</b>
          </p>
          <ul>
            <li>Raum: {{ cancelationData.title }}</li>
            <li v-if="cancelationData.summary">
              Anlass: {{ cancelationData.summary }}
            </li>
            <li>Datum: {{ cancelationData.date }}</li>
          </ul>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Nein, abbrechen" color="primary" v-close-popup />
          <q-btn
            flat
            label="Ja, Stornieren!"
            color="primary"
            v-close-popup
            @click="cancelReservation(cancelationData)"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="cancelationError">
      <q-card>
        <q-card-section>
          <div class="text-h6">Fehler</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          Die Reservation konnte nicht storniert werden.<br />
          Grund: {{ cancelationErrorMsg }}
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="OK"
            color="primary"
            v-close-popup
            @click="fetchData()"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-page-sticky position="bottom-right" :offset="[18, 18]">
      <q-btn fab icon="add" color="accent" to="/reservation/add" />
    </q-page-sticky>
  </q-page>
</template>

<script setup lang="ts">
import { date } from 'quasar'
import { computed, onMounted, reactive, ref } from 'vue'

import { api } from 'boot/axios'
import { useAuthStore } from 'stores/auth-store'

const authStore = useAuthStore()

function cancelReservation(res: any): void {
  console.log('Cancel id ' + res.id)
  api
    .post(
      '/api/v1/reservation/edit/',
      {
        action: 'cancel',
        reservationId: res.id,
      },
      {
        headers: {
          Authorization: 'Bearer ' + authStore.accessToken,
        },
      }
    )
    .then((response) => {
      //console.log(response);
      apiError.value = ''
      console.log(response.data)
      if (response.data.status == 'OK') {
        res.canEdit = false
        res.cancelled = true
      } else {
        cancelationError.value = true
        cancelationErrorMsg.value = response.data.msg
      }
    })
    .catch((error) => {
      apiError.value = 'Es ist ein Fehler aufgetreten.'
      cancelationError.value = true
      cancelationErrorMsg.value = 'Fehler beim Speichern.'
      if ('response' in error) {
        console.log('ERROR: ' + error.response.data.detail)
        if (
          error.response.data.detail == 'Anmeldedaten fehlen.' ||
          error.response.data.detail == 'Ungültiges Token'
        ) {
          // Auth missing -> Force new login
          //console.log("DISABLED FOR DEBUGGING: Force logout");
          authStore.logout()
        }
      } else {
        console.log('ERROR: ' + error)
      }
    })
}

function editReservation(res: any): void {
  // Show cancellation dialog
  confirmCancelation.value = true
  cancelationData.value = res
}

function fetchData(): void {
  api
    .get('/api/v1/reservation/reservations/', {
      headers: {
        Authorization: 'Bearer ' + authStore.accessToken,
      },
    })
    .then((response) => {
      //console.log(response);
      apiError.value = ''
      const now = Date.now()
      reservations.length = 0
      past_reservations.length = 0
      for (let i in response.data.results) {
        let r = response.data.results[i]
        /*console.log(r);
        console.log(r.name);*/
        const date_start = new Date(r.date_start)
        const date_end = new Date(r.date_end)
        const res_data = {
          canEdit: r.can_edit,
          date:
            date.formatDate(date_start, 'DD.MM.YYYY HH:mm') +
            ' – ' +
            date.formatDate(date_end, 'DD.MM.YYYY HH:mm'),
          id: r.id,
          summary: r.summary,
          title: r.name,
        }
        if (date_end.getTime() > now) {
          reservations.push(res_data)
        } else {
          past_reservations.push(res_data)
        }
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
          // Auth missing -> Force new login
          //console.log("DISABLED FOR DEBUGGING: Force logout");
          authStore.logout()
        }
      } else {
        console.log('ERROR: ' + error)
      }
    })
}

const apiError = ref('')

const confirmCancelation = ref(false)
const cancelationData = ref<any>({})
const cancelationError = ref(false)
const cancelationErrorMsg = ref('')

const past_reservations = reactive<any[]>([])
const reservations = reactive<any[]>([]) /*
  {
    id: "1000",
    title: "Gästezimmer 003",
    date: "12.10.2022 - 13.10.2022",
    canEdit: true,
  },
  {
    id: "1001",
    title: "Gästezimmer 410",
    date: "22.09.2022 - 05.10.2022",
    canEdit: false,
  },
  {
    id: "1002",
    title: "Gästezimmer 509",
    date: "22.03.2022 - 01.04.2021",
    canEdit: false,
  },
]);*/
onMounted(() => {
  fetchData()
})

const hasReservations = computed(() => {
  return reservations.length
})
const hasPastReservations = computed(() => {
  return past_reservations.length
})
</script>
