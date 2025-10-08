<template>
  <q-page padding class="">
    <h4 class="q-my-md">{{ $t('reservationEditPage.title') }}</h4>

    <div class="row flex justify-between" v-if="reservationTypeOptions.length">
      <q-select
        class="col-xs-12 q-pb-xs"
        v-model="reservationType"
        @update:model-value="formUpdated('type')"
        :options="reservationTypeOptions.map((x) => x.name)"
        :label="$t('reservationEditPage.whatToReserve')"
      />

      <q-input
        v-model="date_start_input"
        @update:model-value="formUpdated('date_start')"
        class="col-xs-6 q-col-gutter-xs col-md-3"
        :class="{ hidden: !reservationType }"
        :label="$t('reservationEditPage.from')"
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
              <q-btn
                v-close-popup
                :label="$t('reservationEditPage.close')"
                color="primary"
                flat
              />
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
              <q-btn
                v-close-popup
                :label="$t('reservationEditPage.close')"
                color="primary"
                flat
              />
            </div>
          </q-time>
        </q-popup-proxy>
      </q-input>

      <q-input
        v-model="date_end"
        @update:model-value="formUpdated('date_end')"
        class="col-xs-6 q-col-gutter-xs col-md-3"
        :label="$t('reservationEditPage.until')"
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
              <q-btn
                v-close-popup
                :label="$t('reservationEditPage.close')"
                color="primary"
                flat
              />
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
              <q-btn
                v-close-popup
                :label="$t('reservationEditPage.close')"
                color="primary"
                flat
              />
            </div>
          </q-time>
        </q-popup-proxy>
      </q-input>
    </div>
    <div class="row flex justify-between" v-else>
      <p>
        {{ $t('reservationEditPage.noPermission') }}
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
              {{ $t('reservationEditPage.reserve') }}
            </q-btn>
            <div v-else>
              {{ $t('reservationEditPage.notAvailable') }}<br />{{
                room.unavailableDate
              }}
            </div>
          </q-card-actions>
        </q-card>
      </div>
    </div>
    <div v-if="hasLinks">
      <p v-if="settings.reservationLinks.note">
        <b>{{ $t('reservationEditPage.note') }}</b>
        {{ settings.reservationLinks.note }}
      </p>
      <h6 class="q-my-xs">{{ $t('reservationEditPage.links') }}</h6>
      <q-list bordered separator>
        <q-item
          v-for="item in settings.reservationLinks.links"
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
          <span class="q-ml-sm text-h6">{{
            $t('reservationEditPage.confirmDialog.title')
          }}</span>
          <ul>
            <li>
              {{ $t('reservationEditPage.confirmDialog.room') }}
              {{ selectedRoom?.title }}
            </li>
            <li>
              {{ $t('reservationEditPage.confirmDialog.date') }}
              {{ $t('reservationEditPage.confirmDialog.dateFrom') }}
              {{ date_start }} {{ time_start }}
              {{ $t('reservationEditPage.confirmDialog.dateTo') }}
              {{ date_end }}
              {{ time_end }}
            </li>
            <li>
              {{ $t('reservationEditPage.confirmDialog.costs') }}:
              {{
                selectedRoom?.costs
                  ? selectedRoom.costs
                  : $t('reservationEditPage.confirmDialog.defaultCost')
              }}
            </li>
          </ul>
          <div class="q-px-md">
            <div class="q-gutter-y-md column" style="max-width: 500px">
              <q-input
                v-if="summaryRequired"
                v-model="reservationSummary"
                :label="$t('reservationEditPage.confirmDialog.reason.label')"
                :placeholder="
                  $t('reservationEditPage.confirmDialog.reason.placeholder')
                "
                required
                counter
                :rules="[
                  (val) =>
                    !!val ||
                    $t('reservationEditPage.confirmDialog.reason.validation'),
                ]"
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
          <q-btn
            flat
            :label="$t('reservationEditPage.confirmDialog.cancelButton')"
            color="primary"
            v-close-popup
          />
          <q-btn
            flat
            :label="$t('reservationEditPage.confirmDialog.reserveButton')"
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
          <div class="text-h6">
            {{ $t('reservationEditPage.errorDialog.title') }}
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          {{ $t('reservationEditPage.errorDialog.message') }}<br />
          {{ $t('reservationEditPage.errorDialog.reason') }}
          {{ submissionErrorMsg }}
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            :label="$t('reservationEditPage.errorDialog.ok')"
            color="primary"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { settings } from 'app/tenant-config/settings'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import { api } from 'boot/axios'
import { useAuthStore } from 'stores/auth-store'

const { t } = useI18n()
const authStore = useAuthStore()
const router = useRouter()

function formUpdated(what: string): void {
  const current_type = reservationTypeOptions.value.find((obj) => {
    return obj.name == reservationType.value
  })

  if (current_type) {
    summaryRequired.value = Boolean(current_type.summary_required)
    fixedTime.value = Boolean(current_type.fixed_time)
    if (current_type.fixed_time) {
      time_start.value = current_type.default_time_start.substring(0, 5)
      time_end.value = current_type.default_time_end.substring(0, 5)
    } else {
      if (what == 'date_start' || (date_start.value && !date_end.value)) {
        date_end.value =
          typeof date_start.value === 'string' ? date_start.value : null
      }
      if (what == 'type') {
        time_start.value = current_type.default_time_start.substring(0, 5)
        time_end.value = current_type.default_time_end.substring(0, 5)
      }
    }
  } else {
    // Handle other reservation type cases
  }

  // Handle range dates for fixed time reservations
  // When range mode is active, q-date returns an object { from: "DD.MM.YYYY", to: "DD.MM.YYYY" }
  if (
    fixedTime.value &&
    date_start.value &&
    typeof date_start.value === 'object' &&
    'from' in date_start.value &&
    'to' in date_start.value
  ) {
    // Extract the actual dates from the range object
    const rangeStart = date_start.value.from
    const rangeEnd = date_start.value.to

    // Update date_start to be just the 'from' date string
    date_start.value = rangeStart
    // Update date_end to be the 'to' date string
    date_end.value = rangeEnd
  }

  // Automatically hide date pickers
  if (dateFromProxy.value && 'hide' in dateFromProxy.value) {
    dateFromProxy.value.hide()
  }
  if (dateToProxy.value && 'hide' in dateToProxy.value) {
    dateToProxy.value.hide()
  }

  // Validation
  let d_start = null
  let d_end = null
  if (date_start.value && typeof date_start.value === 'string') {
    date_start_error.value = false
    if (/^[0-3]\d\.[0-1]\d\.[\d]+$/.test(date_start.value)) {
      d_start = str2date(date_start.value, time_start.value ?? undefined)
      //console.log(d_start);
    } else {
      //console.log("Invalid date: " + date_start.value);
      date_start_error.value = true
    }
    if (d_start && d_start.getTime() < Date.now()) {
      date_start_error.value = true
    }
  }
  if (date_end.value) {
    date_end_error.value = false
    time_end_error.value = false
    if (/^[0-3]\d\.[0-1]\d\.[\d]+$/.test(date_end.value)) {
      d_end = str2date(date_end.value, time_end.value ?? undefined)
      //console.log(d_end);
    } else {
      //console.log("Invalid date: " + date_end.value);
      date_end_error.value = true
    }
    if (d_start && d_end && d_start.getTime() > d_end.getTime()) {
      if (date_start.value == date_end.value) {
        time_end_error.value = true
      } else {
        date_end_error.value = true
      }
    }
  }
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

function getReservationTypes() {
  api
    .get('/api/v1/reservation/reservationtypes/')
    .then((response) => {
      apiError.value = ''
      reservationTypeOptions.value = response.data.results
      if (reservationTypeOptions.value.length) {
        if (!reservationType.value) {
          // Take first as default
          reservationType.value = reservationTypeOptions.value[0]?.name || null
        }
        formUpdated('type')
      }
    })
    .catch((error) => {
      apiError.value = t('reservationEditPage.errors.general')
      if ('response' in error) {
        if (
          error.response.data.detail ==
            t('reservationEditPage.errors.missingCredentials') ||
          error.response.data.detail ==
            t('reservationEditPage.errors.invalidToken')
        ) {
          // Auth missing -> Force new login
          //console.log("DISABLED FOR DEBUGGING: Force logout");
          authStore.logout()
        }
      }
    })
}

function reservationSearch() {
  // Ensure we're using string values, not range objects
  let dateFromValue = date_start.value
  let dateToValue = date_end.value

  // Handle case where date_start might still be a range object
  if (
    dateFromValue &&
    typeof dateFromValue === 'object' &&
    'from' in dateFromValue
  ) {
    dateToValue = dateFromValue.to
    dateFromValue = dateFromValue.from
  }

  console.log(
    'Reservation search: ' +
      reservationType.value +
      ' / ' +
      dateFromValue +
      ' ' +
      time_start.value +
      ' - ' +
      dateToValue +
      ' ' +
      time_end.value
  )
  api
    .get('/api/v1/reservation/search/', {
      params: {
        dateFrom: dateFromValue,
        dateTo: dateToValue,
        reservationType: reservationType.value,
        timeFrom: time_start.value,
        timeTo: time_end.value,
      },
    })
    .then((response) => {
      apiError.value = ''
      searchResult.value = response.data
    })
    .catch((error) => {
      apiError.value = t('reservationEditPage.errors.general')
      if ('response' in error) {
        if (
          error.response.data.detail ==
            t('reservationEditPage.errors.missingCredentials') ||
          error.response.data.detail ==
            t('reservationEditPage.errors.invalidToken')
        ) {
          // Auth missing -> Force new login
          //console.log("DISABLED FOR DEBUGGING: Force logout");
          authStore.logout()
        }
      }
    })
}

function roomSelect(room: Room): void {
  selectedRoom.value = room
  confirmReservation.value = true
}

function str2date(date_string: string, time_string?: string): Date {
  const ds = date_string.split('.')
  if (time_string) {
    const ts = time_string.split(':')
    return new Date(
      Number(ds[2]),
      Number(ds[1]) - 1,
      Number(ds[0]),
      Number(ts[0]),
      Number(ts[1])
    )
  } else {
    return new Date(Number(ds[2]), Number(ds[1]) - 1, Number(ds[0]))
  }
}

function submitReservation() {
  // Ensure we're using string values, not range objects
  let dateFromValue = date_start.value
  let dateToValue = date_end.value

  // Handle case where date_start might still be a range object
  if (
    dateFromValue &&
    typeof dateFromValue === 'object' &&
    'from' in dateFromValue
  ) {
    dateToValue = dateFromValue.to
    dateFromValue = dateFromValue.from
  }

  api
    .post('/api/v1/reservation/edit/', {
      action: 'add',
      dateFrom: dateFromValue,
      dateTo: dateToValue,
      reservationType: reservationType.value,
      selectedRoom: selectedRoom.value?.id ?? null,
      summary: reservationSummary.value,
      timeFrom: time_start.value,
      timeTo: time_end.value,
    })
    .then((response) => {
      apiError.value = ''
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
      apiError.value = t('reservationEditPage.errors.general')
      submissionError.value = true
      submissionErrorMsg.value = t('reservationEditPage.errors.saveFailed')
      if ('response' in error) {
        if (
          error.response.data.detail ==
            t('reservationEditPage.errors.missingCredentials') ||
          error.response.data.detail ==
            t('reservationEditPage.errors.invalidToken')
        ) {
          // Auth missing -> Force new login
          //console.log("DISABLED FOR DEBUGGING: Force logout");
          authStore.logout()
        }
      }
    })
}

onMounted(() => {
  getReservationTypes()
})

// Type for date range when using range mode
interface DateRange {
  from: string
  to: string
}

interface PopupProxy {
  hide(): void
}

// Interface definitions
interface ReservationType {
  default_time_end: string
  default_time_start: string
  fixed_time?: boolean
  name: string
  summary_required?: boolean
}

interface Room {
  costs?: string
  id: number
  imageUrl: string
  isAvailable: boolean
  subtitle: string
  text: string
  title: string
  unavailableDate?: string
}

// Search and select room
const reservationType = ref<null | string>(null)
const fixedTime = ref(true)
const summaryRequired = ref(false)
const reservationTypeOptions = ref<ReservationType[]>([])
const date_start = ref<DateRange | null | string>(null) // Can be string or range object
const date_start_error = ref(false)
const date_end = ref<null | string>(null)
const date_end_error = ref(false)
const date_end_errormsg = ref('Datum ungültig')
const time_start = ref<null | string>(null)
const time_end = ref<null | string>(null)
const time_end_error = ref(false)
const dateFromProxy = ref<null | PopupProxy>(null)
const dateToProxy = ref<null | PopupProxy>(null)
const searchResult = ref<null | Room[]>(null)
const selectedRoom = ref<null | Room>(null)
const apiError = ref('')

const hasLinks = settings.reservationLinks.links.length > 0

// Computed property to ensure date_start is always string | null for inputs
const date_start_input = computed({
  get: () => (typeof date_start.value === 'string' ? date_start.value : null),
  set: (val: null | string) => {
    date_start.value = val
  },
})

// Dialogs
const confirmReservation = ref(false)
const reservationSummary = ref('')
const submissionError = ref(false)
const submissionErrorMsg = ref('')
</script>
