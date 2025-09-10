<template>
  <q-page padding class="">
    <div>
      <q-select
        outlined
        v-model="viewSelect"
        label="Kalender-Ansicht"
        :options="viewOptions"
        :dense="true"
        :options-dense="true"
        @update:model-value="selectView()"
      >
        <template v-slot:prepend>
          <q-icon name="event" />
        </template>
      </q-select>
    </div>
    <div v-if="filterEnabled">
      <q-select
        outlined
        v-model="activeEventSources"
        :options="eventSourceOptions"
        label="Filter"
        :dense="true"
        :options-dense="true"
        multiple
        emit-value
        map-options
        @update:model-value="updateEventSources()"
      >
        <template v-slot:prepend>
          <q-icon name="filter_alt" />
        </template>
        <template v-slot:option="{ itemProps, opt, selected, toggleOption }">
          <q-item v-bind="itemProps" :class="opt.class">
            <q-item-section>
              <q-item-label>{{ opt.label }}</q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-toggle
                :model-value="selected"
                @update:model-value="toggleOption(opt)"
              />
            </q-item-section>
          </q-item>
        </template>
      </q-select>
    </div>

    <FullCalendar ref="fullCalendar" :options="calendarOptions" />

    <q-page-sticky position="bottom-right" :offset="[18, 18]">
      <q-btn fab icon="add" color="accent" to="/reservation/add" />
    </q-page-sticky>
  </q-page>
</template>

<script setup lang="ts">
import dayGridPlugin from '@fullcalendar/daygrid'
import listPlugin from '@fullcalendar/list'
import timeGridPlugin from '@fullcalendar/timegrid'
import '@fullcalendar/core/vdom' // solves problem with Vite
import FullCalendar from '@fullcalendar/vue3'
import tippy from 'tippy.js'
import { onMounted, ref } from 'vue'

import { api } from 'boot/axios'
import 'tippy.js/dist/tippy.css'

function fetchData() {
  // Get calendar event sources
  api
    .get('/api/v1/reservation/calendar_feeds/')
    .then((response) => {
      if (response.data.status == 'OK') {
        apiError.value = ''
        eventSources.value = response.data.calendars
        let calApi = fullCalendar.value?.getApi()
        if (calApi) {
          for (let es in eventSources.value) {
            calApi.addEventSource(eventSources.value[es])
          }
        }
      } else {
        apiError.value = 'Fehler beim Abrufen der CalendarFeeds.'
      }
    })
    .catch((error) => {
      apiError.value = 'Es ist ein Fehler aufgetreten.'
      if ('response' in error) {
        if (error.response.data.detail == 'Anmeldedaten fehlen.') {
          // Auth missing -> Force new login
          //authStore.logout();
        }
      }
    })
}

function selectView(): void {
  let calApi = fullCalendar.value?.getApi()
  calApi?.changeView(viewSelect.value?.value)
}

function updateEventSources(): void {
  // Update event sources when filter changes
  const calApi = fullCalendar.value?.getApi()
  if (calApi) {
    // Remove existing event sources
    const currentSources = calApi.getEventSources()
    currentSources.forEach((source) => source.remove())

    // Add filtered event sources
    eventSources.value.forEach((source) => {
      if (
        activeEventSources.value.includes(source.id) ||
        activeEventSources.value.includes('all')
      ) {
        calApi.addEventSource(source)
      }
    })
  }
}

const apiError = ref('')

const calendarOptions = {
  allDayContent: { html: '<small>Ganztags</small>' },
  aspectRatio: 0.8,
  //defaultDate: '2017-11-12',
  buttonText: {
    day: 'Tag',
    list: 'Liste',
    month: 'Monat',
    today: 'Heute',
    week: 'Woche',
  },
  editable: false,
  eventDidMount: function (info: any) {
    tippy(info.el, {
      //placement: "top",
      //trigger: "hover",
      //container: "body",
      allowHTML: true,
      content: info.event.extendedProps.description,
    })
  },
  firstDay: 1,
  headerToolbar: {
    left: 'title',
    right: 'today prev,next',
  },
  initialView: 'dayGridWeek', //"dayGridMonth",
  locale: 'de-ch',
  navLinks: true, // can click day/week names to navigate views
  noEventsContent: { html: 'Keine Termine' },
  plugins: [dayGridPlugin, timeGridPlugin, listPlugin],
  views: {
    week: {},
  },
  weekends: true,
}

const viewOptions = [
  {
    category: '1',
    description: 'blabla Test',
    label: 'Monat',
    value: 'dayGridMonth',
  },
  {
    category: '1',
    description: 'blabla Test',
    label: 'Woche - Übersicht',
    value: 'dayGridWeek',
  },
  {
    category: '1',
    description: 'blabla Test',
    label: 'Woche - Zeitraster',
    value: 'timeGridWeek',
  },
  {
    category: '1',
    description: 'blabla Test',
    label: 'Tag',
    value: 'timeGridDay',
  },
  {
    category: '1',
    description: 'blabla Test',
    label: 'Liste',
    value: 'listMonth',
  },
]
const viewSelect = ref(viewOptions[1])
const fullCalendar = ref<any>(null)
const filterEnabled = ref(false)
const eventSourceOptions = [
  {
    class: 'text-bold',
    label: 'Alle',
    value: 'all',
  },
  {
    category: 'top',
    label: 'Genossenschaft',
    value: 'Genossenschaft',
  },
  {
    category: 'Genossenschaft',
    class: 'q-px-xl',
    label: 'Plena, GV etc.',
    value: 'plena',
  },
  {
    category: 'top',
    label: 'Reservation',
    value: 'Reservation',
  },
  {
    category: 'Reservation',
    class: 'q-px-xl',
    label: 'Gästezimmer',
    value: '_res-1',
  },
]
const eventSources = ref<any[]>([])
const activeEventSources = ref<any[]>([])

onMounted(() => {
  fetchData()
})
</script>

<style lang="css">
.q-page-sticky {
  z-index: 100;
}
.fc .fc-toolbar-title {
  font-size: 1.2em;
}
</style>
