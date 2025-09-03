<template>
  <q-page padding class="">
    <!-- <q-page class="flex flex-center">-->
    <!--<h4 class="q-mx-xs q-my-md">Deine Reservationen</h4>-->
    Meldung von:<br />{{ contact }}
    <q-form @submit="submitReport()">
      <q-select
        v-model="unit"
        label="Betroffene Wohnung/Raum"
        :options="unitOptions"
        :dense="dense"
        :loading="formLoading"
        :rules="[(val) => !!val || 'Pflichtfeld']"
      ></q-select>
      <q-select
        v-model="category"
        label="Betroffener Bereich/Bauteil"
        :options="categoryOptions"
        :dense="dense"
        :loading="formLoading"
        :rules="[(val) => !!val || 'Pflichtfeld']"
      ></q-select>
      <q-input
        v-model="subject"
        label="Betreff"
        placeholder="Ein paar Stichworte um was es geht"
        :dense="dense"
        :rules="[(val) => !!val || 'Pflichtfeld']"
        maxlength="60"
      />
      <q-input
        v-model="text"
        label="Beschreibung des Schadens"
        placeholder="Möglichst genaue Beschreibung des Schadens/Problems"
        :dense="dense"
        type="textarea"
        :rules="[(val) => !!val || 'Pflichtfeld']"
      />
      <q-input
        v-model="contact_text"
        label="Erreichbarkeit"
        placeholder="Wann und wie bist du am besten erreichbar?"
        :dense="dense"
        :rules="[(val) => !!val || 'Pflichtfeld']"
        maxlength="300"
      />
      <q-file
        v-model="pictures"
        label="Bilder hinzufügen"
        counter
        max-files="5"
        multiple
        append
        clearable
        accept=".jpg, image/*"
        @rejected="onRejected"
        sstyle="max-width: 300px"
      >
        <template v-slot:prepend>
          <q-icon name="image" />
        </template>
      </q-file>
      <q-btn
        :loading="is_submitting"
        :disabled="submissionDisabled"
        label="Absenden"
        color="primary"
        type="submit"
      />
    </q-form>
    <div
      v-if="apiError"
      class="q-mt-md text-subtitle-1 text-negative text-center full-width"
    >
      <div>
        <q-icon name="warning" size="2em" />
      </div>
      <div>{{ apiError }}</div>
    </div>
    <q-dialog v-model="submissionError">
      <q-card>
        <q-card-section>
          <div class="text-h6">Fehler</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          Die Meldung konnte nicht übermittelt werden.<br />
          Grund: {{ submissionErrorMsg }}
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="OK" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
    <q-dialog v-model="submissionOK">
      <q-card>
        <q-card-section>
          <div class="text-h6">Vielen Dank!</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          Die Meldung wurde erfolgreich übermittelt.
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="OK"
            color="primary"
            v-close-popup
            @click="submitConfirmed()"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { api } from 'boot/axios'
import { useQuasar } from 'quasar'
import { useAuthStore } from 'stores'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const quasar = useQuasar()
const authStore = useAuthStore()
const router = useRouter()

function fetchData() {
  api
    .get('/api/v1/reservation/report/', {
      headers: {
        Authorization: 'Token ' + authStore.token,
      },
    })
    .then((response) => {
      //console.log(response);
      apiError.value = ''
      contact.value = response.data.contact
      unitOptions.value = response.data.rental_units.concat(unitOptions.value)
      unit.value = unitOptions.value[0]
      categoryOptions.value = response.data.categories
      formLoading.value = false
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

function onRejected(entries) {
  if (entries[0].failedPropValidation == 'max-files') {
    quasar.notify('Es können max. 5 Bilder hinzugefügt werden.')
  } else {
    quasar.notify('Ungültige Datei')
  }
}

function submitReport() {
  //console.log("Submit reservation");
  is_submitting.value = true
  let formData = new FormData()
  formData.append('action', 'add')
  formData.append('unit', unit.value.value)
  formData.append('category', category.value.value)
  formData.append('subject', subject.value)
  formData.append('contact_text', contact_text.value)
  formData.append('text', text.value)
  for (let pic in pictures.value) {
    formData.append('pictures', pictures.value[pic])
  }
  api
    .post('/api/v1/reservation/report/', formData, {
      headers: {
        Authorization: 'Token ' + authStore.token,
      },
    })
    .then((response) => {
      apiError.value = ''
      //console.log(response);
      //console.log(response.data);
      if (response.data.status == 'ERROR') {
        submissionError.value = true
        submissionErrorMsg.value = response.data.msg
      } else if (response.data.status == 'OK') {
        submissionOK.value = true
        submissionDisabled.value = true // Prevent re-submission
      }
      is_submitting.value = false
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
      is_submitting.value = false
    })
}

function submitConfirmed() {
  router.go(-1)
}

const apiError = ref('')
const dense = ref(false)
const formLoading = ref(true)

// For axios post file upload fields
const unit = ref(null)
const category = ref(null)
const subject = ref('')
const contact_text = ref('')
const text = ref('')
const pictures = ref([])

// Loaded on fetch
const contact = ref('')
const unitOptions = ref([
  //{ label: "Wohnung 011", value: "011" },
  {
    label: 'Etwas anderes (bitte unter Betreff angeben)',
    value: '__OTHER__',
  },
])
const categoryOptions = ref([
  /*{
    label: "Küche",
    value: "Küche",
  },
  {
    label: "Fenster",
    value: "Fenster",
  },
  {
    label: "Boden",
    value: "Boden",
  },*/
])

const is_submitting = ref(false)
const submissionDisabled = ref(false)
const submissionError = ref(false)
const submissionErrorMsg = ref('')
const submissionOK = ref(false)

onMounted(() => {
  fetchData()
})
</script>
