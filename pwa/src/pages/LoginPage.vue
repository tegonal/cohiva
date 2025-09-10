<template>
  <q-page>
    <div class="flex flex-center">
      <img
        :alt="settings.SITE_NICKNAME + ' Logo'"
        src="/src/assets/logo.svg"
        style="width: 200px; height: 200px"
      />
    </div>
    <div class="row flex-center q-px-md">
      <div class="col-xs-12 col-sm-8 col-md-6 col-lg-4 text-center">
        <h6>Melde dich mit deinem {{ settings.SITE_NICKNAME }}-Konto an:</h6>

        <!-- Backend Status Message -->
        <div v-if="checkingBackend" class="full-width q-my-md text-center">
          <q-spinner color="primary" size="2em" />
          <div class="q-mt-sm">Verbindung zum Server wird geprüft...</div>
        </div>

        <div v-else-if="authStore.backendError" class="full-width q-my-md">
          <q-banner class="bg-negative text-white text-left" rounded>
            <template v-slot:avatar>
              <q-icon name="error" color="white" />
            </template>
            <div class="text-subtitle1">Backend-Server nicht erreichbar</div>
            <div class="q-mt-sm">{{ authStore.backendError }}</div>
            <template v-slot:action>
              <q-btn
                flat
                color="white"
                label="Erneut versuchen"
                @click="retryBackendCheck"
              />
            </template>
          </q-banner>
        </div>

        <!-- OAuth Login Button -->
        <div class="row">
          <q-btn
            color="primary"
            class="full-width q-my-md"
            size="lg"
            @click="loginWithOAuth()"
            :disabled="isLoading || checkingBackend || !!authStore.backendError"
          >
            <q-spinner
              v-if="isLoading"
              color="white"
              size="1em"
              class="q-mr-sm"
            />
            <q-icon v-else name="login" class="q-mr-sm" />
            Mit {{ settings.SITE_NICKNAME }} anmelden
          </q-btn>

          <div
            v-if="error"
            class="q-mt-md text-subtitle-1 text-negative text-center full-width"
          >
            <div>
              <q-icon name="warning" size="2em" />
            </div>
            <div>{{ error }}</div>
          </div>

          <p class="q-mt-lg text-center full-width text-grey-6 text-body2">
            Du wirst zur sicheren Anmeldeseite weitergeleitet.
          </p>

          <p class="q-mt-md text-center full-width text-grey-6 text-subtitle-1">
            <a :href="settings.PASSWORD_RESET_LINK">Passwort vergessen?</a>
          </p>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from 'stores/auth-store'

import { settings } from '../../config/settings'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const isLoading = ref(false)
const error = ref('')
const checkingBackend = ref(false)

onMounted(async () => {
  // First check backend health
  checkingBackend.value = true
  await authStore.checkBackendHealth()
  checkingBackend.value = false

  // Check if user is already authenticated
  const isAuth = await authStore.checkAuth()
  if (isAuth) {
    // Redirect to home or return URL
    const returnUrl = route.query.returnUrl || authStore.returnUrl || '/'
    router.push(returnUrl as string)
  }
})

async function loginWithOAuth() {
  isLoading.value = true
  error.value = ''

  try {
    // Get return URL from query params or store
    const returnUrl = route.query.returnUrl || authStore.returnUrl || '/'

    // Start OAuth login flow
    await authStore.login(returnUrl as string)
    // Note: This will redirect to the OAuth provider, so the promise won't resolve
  } catch (err) {
    console.error('OAuth login error:', err)
    error.value = 'Anmeldung fehlgeschlagen. Bitte versuche es erneut.'
    isLoading.value = false
  }
}

async function retryBackendCheck() {
  checkingBackend.value = true
  await authStore.checkBackendHealth()
  checkingBackend.value = false
}
</script>
