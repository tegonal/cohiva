<template>
  <q-page padding class="">
    <!-- <q-page class="flex flex-center">-->
    <h4 class="q-my-md">Neue Reservation</h4>

    <div class="row flex justify-between" v-if="reservationTypeOptions.length">
      <q-select
        class="col-xs-12 q-pb-xs"
        v-model="reservationType"
        @update:model-value="formUpdated('type')"
        :options="reservationTypeOptions.map((x) => x.name)"
        label="Was möchtest du reservieren?"
      />

      <q-input
        v-model="date_start"
        @update:model-value="formUpdated('date_start')"
        class="col-xs-6 q-col-gutter-xs col-md-3"
        :class="{ hidden: !reservationType }"
        label="Von"
        mask="##.##.####"
        :error="date_start_error"
      >
        <template v-slot:append>
          <q-icon name="event" class="cursor-pointer"> </q-icon>
        </template>
        <q-popup-proxy
          cover
          transition-show="scale"
          transition-hide="scale"
          ref="dateFromProxy"
        >
          <q-date
            v-model="date_start"
            mask="DD.MM.YYYY"
            @update:model-value="formUpdated('date_start')"
            :range="fixedTime"
          >
            <div class="row items-center justify-end">
              <q-btn v-close-popup label="Schliessen" color="primary" flat />
            </div>
          </q-date>
        </q-popup-proxy>
      </q-input>
      <q-input
        v-model="time_start"
        @update:model-value="formUpdated('time_start')"
        class="col-xs-6 q-col-gutter-xs col-md-3"
        :class="{ hidden: !reservationType }"
        :readonly="fixedTime"
        label=""
        mask="time"
        :rules="['time']"
      >
        <template v-slot:append>
          <q-icon name="access_time" class="cursor-pointer"> </q-icon>
        </template>
        <q-popup-proxy
          cover
          transition-show="scale"
          transition-hide="scale"
          v-if="!fixedTime"
        >
          <q-time
            v-model="time_start"
            @update:model-value="formUpdated('time_start')"
            mask="HH:mm"
          >
            <div class="row items-center justify-end">
              <q-btn v-close-popup label="Schliessen" color="primary" flat />
            </div>
          </q-time>
        </q-popup-proxy>
      </q-input>

      <q-input
        v-model="date_end"
        @update:model-value="formUpdated('date_end')"
        class="col-xs-6 q-col-gutter-xs col-md-3"
        label="Bis"
        mask="##.##.####"
        :error="date_end_error"
        :error_message="date_end_errormsg"
      >
        <template v-slot:append>
          <q-icon name="event" class="cursor-pointer"> </q-icon>
        </template>
        <q-popup-proxy
          cover
          transition-show="scale"
          transition-hide="scale"
          ref="dateToProxy"
        >
          <q-date
            v-model="date_end"
            mask="DD.MM.YYYY"
            @update:model-value="formUpdated('date_end')"
          >
            <div class="row items-center justify-end">
              <q-btn v-close-popup label="Schliessen" color="primary" flat />
            </div>
          </q-date>
        </q-popup-proxy>
      </q-input>
      <q-input
        v-model="time_end"
        @update:model-value="formUpdated('time_end')"
        class="col-xs-6 q-col-gutter-xs col-md-3"
        label=""
        mask="time"
        :rules="['time']"
        :readonly="fixedTime"
        :error="time_end_error"
      >
        <template v-slot:append>
          <q-icon name="access_time" class="cursor-pointer"> </q-icon>
        </template>
        <q-popup-proxy
          cover
          transition-show="scale"
          transition-hide="scale"
          v-if="!fixedTime"
        >
          <q-time
            v-model="time_end"
            @update:model-value="formUpdated('time_end')"
            format24h
            mask="HH:mm"
          >
            <div class="row items-center justify-end">
              <q-btn v-close-popup label="Schliessen" color="primary" flat />
            </div>
          </q-time>
        </q-popup-proxy>
      </q-input>
    </div>
    <div class="row flex justify-between" v-else>
      <p>
        Es gibt nichts, was du hier reservieren könntest. Möglicherweise fehlt
        dir die nötige Berechtigung.
      </p>
    </div>
    <!-- <q-date
      class="q-ma-md"
      :class="{ hidden: !reservationType }"
      v-model="date"
      @range-end="reservationSearch()"
      range
      subtitle="Wähle Start und Enddatum"
      today-btn
    />-->
    <!-- <div class="q-pb-sm">
      Datum: {{ date_start }} {{ time_start }} - {{ date_end }}
      {{ time_end }} Typ:
      {{ reservationType }}
    </div> -->
    <div
      v-if="apiError"
      class="q-mt-md text-subtitle-1 text-negative text-center full-width"
    >
      <div>
        <q-icon name="warning" size="2em" />
      </div>
      <div>{{ apiError }}</div>
    </div>
    <div class="row flex">
      <div
        v-for="room in searchResult"
        :key="room.id"
        class="room-card col-xs-12 col-md-6 col-lg-4"
      >
        <q-card class="q-ma-md">
          <q-img :src="room.imageUrl" />

          <q-card-section>
            <div class="row no-wrap items-center">
              <div class="col text-h6 ellipsis">
                {{ room.title }}{{ room.costs ? ' &ndash; ' + room.costs : '' }}
              </div>
              <div
                class="col-auto text-grey text-caption q-pt-md row no-wrap items-center"
              ></div>
            </div>
          </q-card-section>

          <q-card-section class="q-pt-none">
            <div class="text-subtitle1">
              {{ room.subtitle }}
            </div>
            <div class="text-caption text-grey">
              <span v-html="room.text"></span>
            </div>
          </q-card-section>

          <q-separator />

          <q-card-actions>
            <q-btn
              flat
              round
              icon="event"
              :disabledd="!room.isAvailable"
              @click="roomSelect(room)"
            />
            <q-btn
              flat
              color="primary"
              v-if="room.isAvailable"
              @click="roomSelect(room)"
            >
              Reservieren
            </q-btn>
            <div v-else>Nicht verfügbar<br />{{ room.unavailableDate }}</div>
          </q-card-actions>
        </q-card>
      </div>
    </div>
    <div v-if="hasLinks">
      <p v-if="settings.RESERVATION_LINKS.NOTE">
        <b>Hinweis:</b> {{ settings.RESERVATION_LINKS.NOTE }}
      </p>
      <h6 class="q-my-xs">Links</h6>
      <q-list bordered separator>
        <q-item
          v-for="item in settings.RESERVATION_LINKS.LINKS"
          :key="item.title"
          clickable
          v-ripple
          :href="item.link"
          target="_blank"
        >
          <q-item-section>
            <q-item-label>{{ item.title }}</q-item-label>
            <q-item-label caption>{{ item.caption }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </div>

    <q-dialog v-model="confirmReservation" persistent>
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="question_mark" color="primary" text-color="white" />
          <span class="q-ml-sm text-h6"
            >Bitte bestätige deine Reservation:</span
          >
          <ul>
            <li>Raum: {{ selectedRoom.title }}</li>
            <li>
              Datum: Von {{ date_start }} {{ time_start }} bis {{ date_end }}
              {{ time_end }}
            </li>
            <li>
              Kosten:
              {{ selectedRoom.costs ? selectedRoom.costs : ' Fr. 0.00' }}
            </li>
          </ul>
          <div class="q-px-md">
            <div class="q-gutter-y-md column" style="max-width: 500px">
              <q-input
                v-if="summaryRequired"
                v-model="reservationSummary"
                label="Anlass/Grund der Reservation"
                placeholder="Kurze Beschreibung"
                required
                counter
                :rules="[(val) => !!val || 'Bitte Feld ausfüllen']"
                minlength="1"
                maxlength="120"
                size="120"
              >
                <template v-slot:prepend
                  ><q-icon name="edit_calendar"></q-icon></template
              ></q-input>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Abbrechen" color="primary" v-close-popup />
          <q-btn
            flat
            label="Reservieren"
            color="primary"
            v-close-popup
            :disabled="summaryRequired && !reservationSummary"
            @click="submitReservation()"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="submissionError">
      <q-card>
        <q-card-section>
          <div class="text-h6">Fehler</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          Die Reservation konnte nicht abgeschlossen werden.<br />
          Grund: {{ submissionErrorMsg }}
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="OK" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { api } from 'boot/axios'
import { useAuthStore } from 'stores'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { settings } from '../../config/settings.js'

const authStore = useAuthStore()
const router = useRouter()

function str2date(date_string, time_string) {
  const ds = date_string.split('.')
  if (time_string) {
    const ts = time_string.split(':')
    return new Date(ds[2], ds[1] - 1, ds[0], ts[0], ts[1])
  } else {
    return new Date(ds[2], ds[1] - 1, ds[0])
  }
}

function formUpdated(what) {
  //console.log("Form updated");

  const current_type = reservationTypeOptions.value.find((obj) => {
    return obj.name == reservationType.value
  })
  /*console.log(current_type);
  console.log(reservationType.value);*/

  if (current_type) {
    summaryRequired.value = current_type.summary_required
    fixedTime.value = current_type.fixed_time
    if (current_type.fixed_time) {
      time_start.value = current_type.default_time_start.substring(0, 5)
      time_end.value = current_type.default_time_end.substring(0, 5)
    } else {
      if (what == 'date_start' || (date_start.value && !date_end.value)) {
        date_end.value = date_start.value
      }
      if (what == 'type') {
        time_start.value = current_type.default_time_start.substring(0, 5)
        time_end.value = current_type.default_time_end.substring(0, 5)
      }
    }
  } else {
    console.error('Current type not found: ' + current_type)
  }

  if (fixedTime.value && date_start.value && date_start.value.from) {
    date_end.value = date_start.value.to
    date_start.value = date_start.value.from
  }

  // Automatically hide date pickers
  if (dateFromProxy.value) {
    dateFromProxy.value.hide()
  }
  if (dateToProxy.value) {
    dateToProxy.value.hide()
  }

  // Validation
  var d_start = null
  var d_end = null
  if (date_start.value) {
    date_start_error.value = false
    if (/^[0-3]\d\.[0-1]\d\.[\d]+$/.test(date_start.value)) {
      d_start = str2date(date_start.value, time_start.value)
      //console.log(d_start);
    } else {
      //console.log("Invalid date: " + date_start.value);
      date_start_error.value = true
    }
    if (d_start && d_start < Date.now()) {
      date_start_error.value = true
    }
  }
  if (date_end.value) {
    date_end_error.value = false
    time_end_error.value = false
    if (/^[0-3]\d\.[0-1]\d\.[\d]+$/.test(date_end.value)) {
      d_end = str2date(date_end.value, time_end.value)
      //console.log(d_end);
    } else {
      //console.log("Invalid date: " + date_end.value);
      date_end_error.value = true
    }
    if (d_start && d_end && d_start > d_end) {
      if (date_start.value == date_end.value) {
        time_end_error.value = true
      } else {
        date_end_error.value = true
      }
    }
  }
  console.log('start: ' + d_start + 'end: ' + d_end)
  if (date_start_error.value || date_end_error.value || time_end_error.value) {
    searchResult.value = null
    return
  }

  if (
    reservationType.value &&
    date_start.value &&
    time_start.value &&
    date_end.value &&
    time_end.value
  ) {
    reservationSearch()
  }
}

function reservationSearch() {
  console.log(
    'Reservation search: ' +
      reservationType.value +
      ' / ' +
      date_start.value +
      ' ' +
      time_start.value +
      ' - ' +
      date_end.value +
      ' ' +
      time_end.value
  )
  api
    .get('/api/v1/reservation/search/', {
      headers: {
        Authorization: 'Token ' + authStore.token,
        /*"X-CSRFTOKEN":
            "NuKLxiCI2BFAnWb3cIhmGjxSz0ZP2icLsJsUnvvG7HNtnILP5TtJ4FFBFI2jk1z2",*/
      },
      params: {
        dateFrom: date_start.value,
        dateTo: date_end.value,
        reservationType: reservationType.value,
        timeFrom: time_start.value,
        timeTo: time_end.value,
      },
    })
    .then((response) => {
      //console.log(response);
      apiError.value = ''
      searchResult.value = response.data
      //console.log(searchResult.value);
      /*const now = Date.now();
      for (let i in response.data.results) {
        let r = response.data.results[i];
        const date_start = new Date(r.date_start);
        const date_end = new Date(r.date_end);
        const res_data = {};
        if (date_end > now) {
          reservations.push(res_data);
        } else {
          past_reservations.push(res_data);
        }
      }*/
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

function roomSelect(room) {
  selectedRoom.value = room
  confirmReservation.value = true
  //console.log("Selected: " + room.id);
}

function submitReservation() {
  //console.log("Submit reservation");
  api
    .post(
      '/api/v1/reservation/edit/',
      {
        action: 'add',
        dateFrom: date_start.value,
        dateTo: date_end.value,
        reservationType: reservationType.value,
        selectedRoom: selectedRoom.value.id,
        summary: reservationSummary.value,
        timeFrom: time_start.value,
        timeTo: time_end.value,
      },
      {
        headers: {
          Authorization: 'Token ' + authStore.token,
        },
      }
    )
    .then((response) => {
      apiError.value = ''
      //console.log(response);
      //console.log(response.data);
      if (response.data.status == 'ERROR') {
        submissionError.value = true
        submissionErrorMsg.value = response.data.msg
        reservationSearch()
      } else {
        // Submission OK -> Go back to previous page
        router.go(-1)
      }
    })
    .catch((error) => {
      apiError.value = 'Es ist ein Fehler aufgetreten.'
      submissionError.value = true
      submissionErrorMsg.value = 'Fehler beim Speichern.'
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

function getReservationTypes() {
  api
    .get('/api/v1/reservation/reservationtypes/', {
      headers: {
        Authorization: 'Token ' + authStore.token,
      },
    })
    .then((response) => {
      apiError.value = ''
      reservationTypeOptions.value = response.data.results
      if (reservationTypeOptions.value.length) {
        if (!reservationType.value) {
          // Take first as default
          reservationType.value = reservationTypeOptions.value[0].name
          //console.log("Set default type: " + reservationType.value);
        }
        formUpdated()
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

onMounted(() => {
  getReservationTypes()
})

// Search and select room
const reservationType = ref(null) //ref(null);
const fixedTime = ref(true)
const summaryRequired = ref(false)
const reservationTypeOptions = ref([])
const date_start = ref(null) // { from: "2022/10/21", to: "2022/10/25" })
const date_start_error = ref(false)
const date_start_errormsg = ref('Datum ungültig')
const date_end = ref(null)
const date_end_error = ref(false)
const date_end_errormsg = ref('Datum ungültig')
const time_start = ref(null)
const time_end = ref(null)
const time_end_error = ref(false)
const dateFromProxy = ref(null)
const dateToProxy = ref(null)
const searchResult = ref(null)
const selectedRoom = ref(null)
const apiError = ref(false)

const hasLinks = settings.RESERVATION_LINKS.LINKS.length > 0

// Dialogs
const confirmReservation = ref(false)
const reservationSummary = ref('')
const submissionError = ref(false)
const submissionErrorMsg = ref('')

// Mockup data
/*const rooms = [
  {
    nr: "003",
    title: "Gästezimmer 003",
    costs: "Fr. 22.00",
    imageUrl: "https://sandammeer.ch/flink/gaestezimmer-003.jpg",
    subtitle: "Familiengästezimmer im Erdgeschoss",
    text: "4(6)+ Schlafplätze (1x 160 cm Bett, 1 x 160 cm Schlafsofa, 1 x Babyreisebett & Wickeltisch). Zusätzliche Matratze (1 x 140) für auf den Boden. 2 Kissen, 4 Duvets, 5 Kissen- & Duvetanzüge, 6 Fixleintücher, 4 Moltons + Baby-Sachen.  Benutzung des öffentlichen Badezimmers (Toiletten und Waschbecken) nebenan. Duschen entweder bei Gastgeber*in oder in den öffentlichen Duschen im Stockwerk -1. Wasserkocher, Kaffeepresse und Tassen. Tisch und Stühle (4).<br /> Preis: 22 CHF / Nacht ab der 4. Nacht.",
    isAvailable: true,
    unavailableDate: "von 12.10.2022 bis 15.10.2022",
  },
  {
    nr: "410",
    title: "Gästezimmer 410",
    costs: "Fr. 17.00",
    imageUrl: "https://sandammeer.ch/flink/gaestezimmer-410.jpg",
    subtitle: "Lesegästezimmer im 4. Stock",
    text: "2 Schlafplätze (1x 160 cm Bett). 2 Kissen, 2 Duvets, 4 Kissen- & Duvetanzüge, 2 Fixleintücher, & 1 Molton. Badezimmer (Toilette und Waschbecken) im Zimmer. Duschen entweder bei Gastgeber*in oder in den öffentlichen Duschen im Stockwerk -1. Tisch und Stühle (2 + Loungesessel).<br /> Preis: 17 CHF / Nacht ab der 4. Nacht.",
    isAvailable: false,
    unavailableDate: "von 12.10.2022 bis 15.10.2022",
  },
  {
    nr: "509",
    title: "Gästezimmer 509",
    costs: "Fr. 17.00",
    imageUrl: "https://sandammeer.ch/flink/gaestezimmer-509.jpg",
    subtitle: "Relaxgästezimmer im 5. Stock",
    text: "2 Schlafplätze (2x 90 cm Bett). 2 Kissen, 2 Duvets, 4 Kissen- & Duvetanzüge, 4 Fixleintücher, & 2 Moltons. Badezimmer (Toilette und Waschbecken) im Zimmer. Duschen entweder bei Gastgeber*in oder in den öffentlichen Duschen im Stockwerk -1. Tisch und Stühle (2 + Loungesessel).<br /> Preis: 17 CHF / Nacht ab der 4. Nacht.",
    isAvailable: true,
    unavailableDate: "von 12.10.2022 bis 15.10.2022",
  },
];*/
</script>
