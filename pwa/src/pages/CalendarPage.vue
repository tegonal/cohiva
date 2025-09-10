<template>
  <q-page padding class="">
    <!-- <q-page class="flex flex-center">-->
    <!--<h4 class="q-mx-xs q-my-md">Deine Reservationen</h4>-->
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
import { useAuthStore } from 'stores/auth-store'
import 'tippy.js/dist/tippy.css'

/*import interactionPlugin from "@fullcalendar/interaction";*/

function fetchData() {
  const authStore = useAuthStore()
  // Get calendar event sources
  api
    .get('/api/v1/reservation/calendar_feeds/')
    .then((response) => {
      //console.log(response);
      if (response.data.status == 'OK') {
        apiError.value = ''
        eventSources.value = response.data.calendars
        let calApi = fullCalendar.value?.getApi()
        if (calApi) {
          for (let es in eventSources.value) {
            console.log('Adding event source ' + eventSources.value[es].id)
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
        console.log('ERROR: ' + error.response.data.detail)
        if (error.response.data.detail == 'Anmeldedaten fehlen.') {
          // Auth missing -> Force new login
          console.log('DISABLED FOR DEBUGGING: Force logout')
          //authStore.logout();
        }
      } else {
        console.log('ERROR: ' + error)
      }
    })
}

function selectView(): void {
  console.log('Switch view to ' + viewSelect.value?.value)
  //let calApi = this.fullCalendar.getApi();
  let calApi = fullCalendar.value?.getApi()
  //console.log("Got calendar API");
  //console.log(calApi);
  calApi?.changeView(viewSelect.value?.value)
  //calApi.next();
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
    /*left: "prev,next today",
    center: "title",
    right:
      "dayGridMonth,dayGridWeek timeGridWeek,timeGridDay listMonth" */
    left: 'title',
    right: 'today prev,next',
  },
  initialView: 'dayGridWeek', //"dayGridMonth",
  locale: 'de-ch',
  navLinks: true, // can click day/week names to navigate views
  noEventsContent: { html: 'Keine Termine' },
  //plugins: [dayGridPlugin, interactionPlugin],
  plugins: [dayGridPlugin, timeGridPlugin, listPlugin],
  //viewDidMount: updateView(),
  views: {
    week: {
      //titleFormat: { year: "2-digit", month: "numeric", day: "numeric" },
      //{year: 'numeric', month: 'numeric', day: 'numeric'}
    },
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
/*const dense = ref(true);
const denseOpts = ref(null);*/
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

/*{
    id: "plena",
    cat: "Genossenschaft",
    name: "Plena, GV, Hausversammlung etc.",
    url: process.env.API + "calendar/feed/plena",
    color: "#4680CD",
    textColor: "black",
  },
  {
    id: "_res-1",
    cat: "Reservation",
    name: "Gästezimmer",
    url: process.env.API + "calendar/feed/_res-1",
    color: "#f8f65d",
    textColor: "black",
  },
  {
    id: "_res-2",
    cat: "Reservation",
    name: "Musikraum",
    url: process.env.API + "calendar/feed/_res-2",
    color: "#33f65d",
    textColor: "black",
  },
  {
    id: "_res-3",
    cat: "Reservation",
    name: "Werkstatt",
    url: process.env.API + "calendar/feed/_res-3",
    color: "#33775d",
    textColor: "black",
  },
];*/

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
