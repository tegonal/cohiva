<template>
  <q-page padding class="">
    {{ $t('repairPage.reportFrom') }}<br />{{ contact }}
    <q-form @submit="submitReport()">
      <q-select
        v-model="unit"
        :label="$t('repairPage.form.affectedUnit.label')"
        :options="unitOptions"
        :dense="dense"
        :loading="formLoading"
        :rules="[(val) => !!val || $t('repairPage.form.requiredField')]"
      ></q-select>
      <q-select
        v-model="category"
        :label="$t('repairPage.form.affectedArea.label')"
        :options="categoryOptions"
        :dense="dense"
        :loading="formLoading"
        :rules="[(val) => !!val || $t('repairPage.form.requiredField')]"
      ></q-select>
      <q-input
        v-model="subject"
        :label="$t('repairPage.form.subject.label')"
        :placeholder="$t('repairPage.form.subject.placeholder')"
        :dense="dense"
        :rules="[(val) => !!val || $t('repairPage.form.requiredField')]"
        maxlength="60"
      />
      <q-input
        v-model="text"
        :label="$t('repairPage.form.description.label')"
        :placeholder="$t('repairPage.form.description.placeholder')"
        :dense="dense"
        type="textarea"
        :rules="[(val) => !!val || $t('repairPage.form.requiredField')]"
      />
      <q-input
        v-model="contact_text"
        :label="$t('repairPage.form.availability.label')"
        :placeholder="$t('repairPage.form.availability.placeholder')"
        :dense="dense"
        :rules="[(val) => !!val || $t('repairPage.form.requiredField')]"
        maxlength="300"
      />
      <q-file
        v-model="pictures"
        :label="$t('repairPage.form.images.label')"
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
        :label="$t('repairPage.form.submitButton')"
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
          <div class="text-h6">{{ $t('repairPage.errorDialog.title') }}</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          {{ $t('repairPage.errorDialog.message') }}<br />
          {{ $t('repairPage.errorDialog.reason') }} {{ submissionErrorMsg }}
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            :label="$t('repairPage.errorDialog.ok')"
            color="primary"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
    <q-dialog v-model="submissionOK">
      <q-card>
        <q-card-section>
          <div class="text-h6">{{ $t('repairPage.successDialog.title') }}</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          {{ $t('repairPage.successDialog.message') }}
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            :label="$t('repairPage.successDialog.ok')"
            color="primary"
            v-close-popup
            @click="submitConfirmed()"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import { api } from 'boot/axios'
import { useAuthStore } from 'stores/auth-store'

const { t } = useI18n()
const quasar = useQuasar()
const authStore = useAuthStore()
const router = useRouter()

function fetchData() {
  api
    .get('/api/v1/reservation/report/')
    .then((response) => {
      apiError.value = ''
      contact.value = response.data.contact
      unitOptions.value = response.data.rental_units.concat(unitOptions.value)
      unit.value = unitOptions.value[0] || null
      categoryOptions.value = response.data.categories
      formLoading.value = false
    })
    .catch((error) => {
      apiError.value = t('repairPage.errors.general')
      if ('response' in error) {
        if (
          error.response.data.detail == t('repairPage.errors.general') ||
          error.response.data.detail == t('repairPage.errors.general')
        ) {
          authStore.logout()
        }
      }
    })
}

function onRejected(entries: any): void {
  if (entries[0].failedPropValidation == 'max-files') {
    quasar.notify(t('repairPage.notifications.maxImages'))
  } else {
    quasar.notify(t('repairPage.notifications.invalidFile'))
  }
}

function submitConfirmed() {
  router.go(-1)
}

function submitReport() {
  is_submitting.value = true
  let formData = new FormData()
  formData.append('action', 'add')
  formData.append('unit', unit.value?.value || '')
  formData.append('category', category.value?.value || '')
  formData.append('subject', subject.value)
  formData.append('contact_text', contact_text.value)
  formData.append('text', text.value)
  for (let pic in pictures.value) {
    if (pictures.value[pic]) {
      formData.append('pictures', pictures.value[pic])
    }
  }
  api
    .post('/api/v1/reservation/report/', formData, {
      transformRequest: [
        (data, headers) => {
          // Remove Content-Type header to let browser set it with boundary for FormData
          if (data instanceof FormData) {
            delete headers['Content-Type']
          }
          return data
        },
      ],
    })
    .then((response) => {
      apiError.value = ''
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
      apiError.value = t('repairPage.errors.general')
      submissionError.value = true
      submissionErrorMsg.value = t('repairPage.errors.saveFailed')
      if ('response' in error) {
        if (
          error.response.data.detail == t('repairPage.errors.general') ||
          error.response.data.detail == t('repairPage.errors.general')
        ) {
          authStore.logout()
        }
      }
      is_submitting.value = false
    })
}

const apiError = ref('')
const dense = ref(false)
const formLoading = ref(true)

// For axios post file upload fields
const unit = ref<any>(null)
const category = ref<any>(null)
const subject = ref('')
const contact_text = ref('')
const text = ref('')
const pictures = ref([])

// Loaded on fetch
const contact = ref('')
const unitOptions = ref([
  {
    label: t('repairPage.form.affectedUnit.otherOption'),
    value: '__OTHER__',
  },
])
const categoryOptions = ref([])

const is_submitting = ref(false)
const submissionDisabled = ref(false)
const submissionError = ref(false)
const submissionErrorMsg = ref('')
const submissionOK = ref(false)

onMounted(() => {
  fetchData()
})
</script>
