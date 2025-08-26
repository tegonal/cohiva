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
        options-dense=""
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
        options-dense=""
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

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "stores";
import { api } from "boot/axios";

import "@fullcalendar/core/vdom"; // solves problem with Vite
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import listPlugin from "@fullcalendar/list";
import tippy from "tippy.js";
import "tippy.js/dist/tippy.css";
/*import interactionPlugin from "@fullcalendar/interaction";*/

function fetchData() {
  const authStore = useAuthStore();
  // Get calendar event sources
  api
    .get("/api/v1/reservation/calendar_feeds/", {
      headers: {
        Authorization: "Token " + authStore.token,
      },
    })
    .then((response) => {
      //console.log(response);
      if (response.data.status == "OK") {
        apiError.value = "";
        eventSources.value = response.data.calendars;
        let calApi = fullCalendar.value.getApi();
        for (let es in eventSources.value) {
          console.log("Adding event source " + eventSources.value[es].id);
          calApi.addEventSource(eventSources.value[es]);
        }
      } else {
        apiError.value = "Fehler beim Abrufen der CalendarFeeds.";
      }
    })
    .catch((error) => {
      apiError.value = "Es ist ein Fehler aufgetreten.";
      if ("response" in error) {
        console.log("ERROR: " + error.response.data.detail);
        if (error.response.data.detail == "Anmeldedaten fehlen.") {
          // Auth missing -> Force new login
          console.log("DISABLED FOR DEBUGGING: Force logout");
          //authStore.logout();
        }
      } else {
        console.log("ERROR: " + error);
      }
    });
}

function selectView() {
  console.log("Switch view to " + viewSelect.value.value);
  //let calApi = this.fullCalendar.getApi();
  let calApi = fullCalendar.value.getApi();
  //console.log("Got calendar API");
  //console.log(calApi);
  calApi.changeView(viewSelect.value.value);
  //calApi.next();
}

const apiError = ref("");

const calendarOptions = {
  //plugins: [dayGridPlugin, interactionPlugin],
  plugins: [dayGridPlugin, timeGridPlugin, listPlugin],
  initialView: "dayGridWeek", //"dayGridMonth",
  headerToolbar: {
    /*left: "prev,next today",
    center: "title",
    right:
      "dayGridMonth,dayGridWeek timeGridWeek,timeGridDay listMonth" */
    left: "title",
    right: "today prev,next",
  },
  aspectRatio: 0.8,
  //defaultDate: '2017-11-12',
  buttonText: {
    today: "Heute",
    month: "Monat",
    week: "Woche",
    day: "Tag",
    list: "Liste",
  },
  locale: "de-ch",
  firstDay: 1,
  allDayContent: { html: "<small>Ganztags</small>" },
  noEventsContent: { html: "Keine Termine" },
  navLinks: true, // can click day/week names to navigate views
  editable: false,
  weekends: true,
  //viewDidMount: updateView(),
  views: {
    week: {
      //titleFormat: { year: "2-digit", month: "numeric", day: "numeric" },
      //{year: 'numeric', month: 'numeric', day: 'numeric'}
    },
  },
  eventDidMount: function (info) {
    new tippy(info.el, {
      content: info.event.extendedProps.description,
      //placement: "top",
      //trigger: "hover",
      //container: "body",
      allowHTML: true,
    });
  },
};

const viewOptions = [
  {
    label: "Monat",
    value: "dayGridMonth",
    description: "blabla Test",
    category: "1",
  },
  {
    label: "Woche - Übersicht",
    value: "dayGridWeek",
    description: "blabla Test",
    category: "1",
  },
  {
    label: "Woche - Zeitraster",
    value: "timeGridWeek",
    description: "blabla Test",
    category: "1",
  },
  {
    label: "Tag",
    value: "timeGridDay",
    description: "blabla Test",
    category: "1",
  },
  {
    label: "Liste",
    value: "listMonth",
    description: "blabla Test",
    category: "1",
  },
];
const viewSelect = ref(viewOptions[1]);
/*const dense = ref(true);
const denseOpts = ref(null);*/
const fullCalendar = ref(null);
const filterEnabled = ref(false);
const eventSourceOptions = [
  {
    label: "Alle",
    value: "all",
    class: "text-bold",
  },
  {
    label: "Genossenschaft",
    value: "Genossenschaft",
    category: "top",
  },
  {
    label: "Plena, GV etc.",
    value: "plena",
    category: "Genossenschaft",
    class: "q-px-xl",
  },
  {
    label: "Reservation",
    value: "Reservation",
    category: "top",
  },
  {
    label: "Gästezimmer",
    value: "_res-1",
    category: "Reservation",
    class: "q-px-xl",
  },
];
const eventSources = ref([]);
const activeEventSources = ref([]);

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
  fetchData();
});
</script>

<style lang="css">
.q-page-sticky {
  z-index: 100;
}
.fc .fc-toolbar-title {
  font-size: 1.2em;
}
</style>
