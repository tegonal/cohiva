<template>
  <q-page padding class="">
    <h4 class="q-mx-xs q-my-md">{{ $t('creditAccountingPage.title') }}</h4>

    <q-expansion-item
      :label="$t('creditAccountingPage.searchFilterLabel')"
      :caption="filterCaption"
      switch-toggle-side
      v-model="expanded"
    >
      <div class="row flex justify-between">
        <q-input
          class="col-xs-12 col-sm-6 col-md-4"
          :label="$t('creditAccountingPage.search')"
          v-model="search"
          debounce="500"
          @update:model-value="formUpdated()"
          maxlength="50"
        >
          <template v-slot:prepend>
            <q-icon name="search" />
          </template>
        </q-input>

        <q-select
          class="col-xs-6 col-sm-3 col-md-2 q-pb-xs"
          v-model="time"
          @update:model-value="formUpdated()"
          :options="timeOptions"
          :label="$t('creditAccountingPage.timeRange')"
        />
        <q-select
          class="col-xs-6 col-sm-3 col-md-2 q-pb-xs"
          v-model="sign"
          @update:model-value="formUpdated()"
          :options="signOptions"
          :label="$t('creditAccountingPage.type')"
        />
        <q-select
          class="col-xs-12 col-sm-6 col-md-4 q-pb-xs"
          v-model="account"
          @update:model-value="formUpdated()"
          :options="accountOptions"
          :label="$t('creditAccountingPage.account')"
          v-if="hasMultipleAccounts"
        />
      </div>

      <div class="q-pt-md" style="text-align: right">
        <q-btn
          color="primary"
          icon="download"
          :label="$t('creditAccountingPage.csvExport')"
          dense
          class="q-mr-sm"
          @click="exportToCSV()"
        />
        <q-btn
          color="primary"
          icon="settings"
          :label="$t('creditAccountingPage.settings')"
          dense
          class=""
          @click="openSettings()"
        />
      </div>
    </q-expansion-item>

    <div class="q-pt-md">
      <q-spinner color="primary" size="3em" v-if="isLoading" />
      <p v-if="maxResults && transactions.length >= maxResults">
        {{ $t('creditAccountingPage.messages.manyTransactions') }}
        <b>{{ maxResults }}</b>
        {{ $t('creditAccountingPage.messages.displayed') }}
      </p>
      <q-markup-table dense>
        <thead>
          <tr>
            <th class="text-left">
              {{ $t('creditAccountingPage.table.date') }}
            </th>
            <th class="text-left">
              {{ $t('creditAccountingPage.table.description') }}
            </th>
            <th class="text-right">
              {{ $t('creditAccountingPage.table.amount') }}
            </th>
            <th class="text-right">
              {{ $t('creditAccountingPage.table.balance') }}
            </th>
            <th class="text-left">
              {{ $t('creditAccountingPage.table.note') }}
            </th>
          </tr>
        </thead>
        <tbody v-if="hasTransactions">
          <tr v-for="transaction in transactions" :key="transaction.id">
            <td class="text-left">{{ transaction.date }}</td>
            <td class="text-left">{{ transaction.name }}</td>
            <td class="text-right">{{ transaction.amount.toFixed(2) }}</td>
            <td class="text-right">{{ transaction.balance.toFixed(2) }}</td>
            <td class="text-left">{{ transaction.note }}</td>
          </tr>
        </tbody>
        <tbody v-else>
          <tr>
            <td colspan="5">
              {{ $t('creditAccountingPage.messages.noTransactions') }}
            </td>
          </tr>
        </tbody>
      </q-markup-table>
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

    <q-page-sticky position="bottom-right" :offset="[18, 18]">
      <q-btn fab icon="add_card" color="accent" @click="paymentDialog = true" />
    </q-page-sticky>

    <q-dialog v-model="paymentDialog" persistent>
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="add_card" color="primary" text-color="white" />
          <span class="q-ml-sm text-h6">{{
            $t('creditAccountingPage.paymentDialog.title')
          }}</span>
          <p class="q-pt-md">
            {{ $t('creditAccountingPage.paymentDialog.instructions') }}
            {{ $t('creditAccountingPage.paymentDialog.accountLabel') }}
            <b>«{{ account.label }}»</b>
            {{ $t('creditAccountingPage.paymentDialog.depositText') }}
            {{ $t('creditAccountingPage.paymentDialog.autoAssignment') }}
          </p>
          <p>
            <q-btn
              :label="$t('creditAccountingPage.paymentDialog.qrSlip')"
              color="primary"
              v-close-popup
              :href="
                api.defaults.baseURL +
                'credit_accounting/accounts/qrbill/' +
                account.value +
                '/'
              "
              target="_blank"
            /></p
        ></q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            :label="$t('creditAccountingPage.paymentDialog.cancel')"
            color="primary"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="settingsDialog" persistent>
      <q-card>
        <q-card-section class="items-center">
          <q-avatar icon="settings" color="primary" text-color="white" />
          <span class="q-ml-sm text-h6"
            >{{ $t('creditAccountingPage.settingsDialog.accountPrefix') }}
            {{ account.label }}</span
          >
        </q-card-section>
        <q-card-section>
          <div>
            <q-input
              class=""
              :label="$t('creditAccountingPage.settingsDialog.pinCode')"
              v-model="settings.pin"
              maxlength="20"
              bottom-slots
            >
              <template v-slot:hint>
                {{ $t('creditAccountingPage.settingsDialog.warning') }}
              </template>
            </q-input>
          </div>
          <div class="q-mt-lg">
            <q-checkbox
              v-model="settings.notification_balance_below_amount_active"
              :label="
                $t('creditAccountingPage.settingsDialog.emailNotification')
              "
            />
          </div>
          <div class="q-pl-sm">
            <q-input
              class=""
              :label="
                $t('creditAccountingPage.settingsDialog.whenBalanceBelow')
              "
              prefix="CHF"
              mask="#"
              fill-mask="0"
              reverse-fill-mask
              v-model="settings.notification_balance_below_amount_value"
              bottom-slots
              :disable="!settings.notification_balance_below_amount_active"
            >
              <template v-slot:hint>
                {{ $t('creditAccountingPage.settingsDialog.emailTo') }}
                <b>{{ settings.user_email }}</b>
                {{ $t('creditAccountingPage.settingsDialog.withQrSlip') }}
              </template>
            </q-input>
          </div>
        </q-card-section>

        <q-card-actions align="right" class="q-mt-lg q-mb-sm">
          <q-btn
            :label="$t('creditAccountingPage.settingsDialog.save')"
            color="primary"
            @click="saveSettings()"
          />
          <q-btn
            flat
            :label="$t('creditAccountingPage.settingsDialog.cancel')"
            color="primary"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { exportFile } from 'quasar'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { api } from 'boot/axios'
import { useAuthStore } from 'stores/auth-store'

const { t } = useI18n()
const authStore = useAuthStore()

function exportToCSV(): void {
  const columns = [
    t('creditAccountingPage.table.date'),
    t('creditAccountingPage.table.description'),
    t('creditAccountingPage.table.amount'),
    t('creditAccountingPage.table.balance'),
    t('creditAccountingPage.table.note'),
  ]
  const content = [columns.map((column) => wrapCsvValue(column))]
    .concat(
      transactions.value.map((transaction) => [
        wrapCsvValue(transaction.date),
        wrapCsvValue(transaction.name),
        wrapCsvValue(transaction.amount.toFixed(2)),
        wrapCsvValue(transaction.balance.toFixed(2)),
        wrapCsvValue(transaction.note),
      ])
    )
    .join('\r\n')

  // TODO: Add account name and date?
  const status = exportFile(
    t('creditAccountingPage.csvExportFilename'),
    content,
    'text/csv'
  )

  if (status !== true) {
    // Handle export error silently
  }
}

function fetchData(): void {
  isLoading.value = true
  api
    .get('/api/v1/credit_accounting/transactions/', {
      params: {
        filter: JSON.stringify({
          account: account.value?.value,
          search: search.value,
          sign: sign.value?.value,
          time: time.value?.value,
        }),
        vendor: 'Depot8',
      },
    })
    .then((response) => {
      isLoading.value = false
      if (response.data.status == 'OK') {
        apiError.value = ''
        transactions.value = response.data.transactions
        maxResults.value = response.data.max_results
      } else {
        apiError.value = t('creditAccountingPage.errors.general')
      }
    })
    .catch((error) => {
      isLoading.value = false
      apiError.value = t('creditAccountingPage.errors.general')
      if ('response' in error) {
        if (
          error.response.data.detail ==
            t('creditAccountingPage.errors.missingCredentials') ||
          error.response.data.detail ==
            t('creditAccountingPage.errors.invalidToken')
        ) {
          authStore.logout()
        }
      }
    })
}

function formUpdated(): void {
  let caption = []
  if (account.value) {
    caption.push(account.value.label)
  }
  if (
    sign.value &&
    sign.value.label != t('creditAccountingPage.filters.allTransactions')
  ) {
    caption.push(sign.value.label)
  }
  if (
    time.value &&
    time.value.label != t('creditAccountingPage.filters.allTransactions')
  ) {
    caption.push(time.value.label)
  }
  if (search.value) {
    caption.push(t('creditAccountingPage.search') + ': ' + search.value)
  }
  filterCaption.value = caption.join(' | ')

  if (account.value && time.value) {
    fetchData()
  }
}

function getAccounts(): void {
  api
    .get('/api/v1/credit_accounting/accounts/', {
      params: {
        vendor: 'Depot8',
      },
    })
    .then((response) => {
      apiError.value = ''
      accountOptions.value = response.data.accounts
      if (!account.value) {
        // Take first as default
        account.value = accountOptions.value[0]
      }
      formUpdated()
    })
    .catch((error) => {
      apiError.value = t('creditAccountingPage.errors.general')
      if ('response' in error) {
        if (
          error.response.data.detail ==
            t('creditAccountingPage.errors.missingCredentials') ||
          error.response.data.detail ==
            t('creditAccountingPage.errors.invalidToken')
        ) {
          authStore.logout()
        }
      }
    })
}

function getFilterOptions(): void {
  api
    .get('/api/v1/credit_accounting/transactions/filter/')
    .then((response) => {
      apiError.value = ''
      timeOptions.value = response.data.time_filter
      if (!time.value) {
        // Take first as default
        time.value = timeOptions.value[0]
      }
      formUpdated()
    })
    .catch((error) => {
      apiError.value = t('creditAccountingPage.errors.general')
      if ('response' in error) {
        if (
          error.response.data.detail ==
            t('creditAccountingPage.errors.missingCredentials') ||
          error.response.data.detail ==
            t('creditAccountingPage.errors.invalidToken')
        ) {
          authStore.logout()
        }
      }
    })
}

function openSettings(): void {
  api
    .get('/api/v1/credit_accounting/settings/', {
      params: { account: account.value?.value, vendor: 'Depot8' },
    })
    .then((response) => {
      if (response.data.status == 'OK') {
        settings.value = response.data.settings
        settingsDialog.value = true
      }
    })
    .catch(() => {
      // Handle error silently
    })
}

function saveSettings(): void {
  api
    .post('/api/v1/credit_accounting/settings/', {
      account: account.value?.value,
      settings: settings.value,
      vendor: 'Depot8',
    })
    .then((response) => {
      if (response.data.status == 'OK') {
        settingsDialog.value = false
      }
    })
    .catch(() => {
      // Handle error silently
    })
}

function wrapCsvValue(val: any, formatFn?: any, _row?: any): string {
  let formatted = formatFn !== void 0 ? formatFn(val, _row) : val

  formatted =
    formatted === void 0 || formatted === null ? '' : String(formatted)

  formatted = formatted.split('"').join('""')
  /**
   * Excel accepts \n and \r in strings, but some other CSV parsers do not
   * Uncomment the next two lines to escape new lines
   */
  // .split('\n').join('\\n')
  // .split('\r').join('\\r')

  return `"${formatted}"`
}

onMounted(() => {
  getAccounts()
  getFilterOptions()
})

const apiError = ref('')

// Filter/search form
const timeOptions = ref<any[]>([])
const signOptions = ref([
  { label: t('creditAccountingPage.filters.allTransactions'), value: 'all' },
  { label: t('creditAccountingPage.filters.credits'), value: 'plus' },
  { label: t('creditAccountingPage.filters.debits'), value: 'minus' },
])
const accountOptions = ref<any[]>([])
const expanded = ref(false)
const filterCaption = ref('')
const search = ref('')
const time = ref<any>(null)
const sign = ref(signOptions.value[0])
const account = ref<any>(null)

const transactions = ref<any[]>([])
const maxResults = ref(0)
const isLoading = ref(false)

const settings = ref({
  notification_balance_below_amount_active: false,
  notification_balance_below_amount_value: 100,
  pin: '',
  user_email: 'test@example.com',
})

const paymentDialog = ref(false)
const settingsDialog = ref(false)

const hasMultipleAccounts = computed(() => {
  return accountOptions.value.length > 1
})
const hasTransactions = computed(() => {
  return transactions.value.length
})
</script>
