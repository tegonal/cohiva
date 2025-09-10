import { register } from 'register-service-worker'
import { useMainStore } from 'src/stores'

// The ready(), registered(), cached(), updatefound() and updated()
// events passes a ServiceWorkerRegistration instance in their arguments.
// ServiceWorkerRegistration: https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerRegistration

register(process.env.SERVICE_WORKER_FILE, {
  // The registrationOptions object will be passed as the second argument
  // to ServiceWorkerContainer.register()
  // https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerContainer/register#Parameter

  // registrationOptions: { scope: './' },

  cached(/* registration */) {
    console.log('Content has been cached for offline use.')
  },

  error(err) {
    console.error('Error during service worker registration:', err)
  },

  offline() {
    console.log('No internet connection found. App is running in offline mode.')
  },

  ready(registration) {
    console.log('Service worker is active.')
    const mainStore = useMainStore()
    mainStore.registration = registration
  },

  registered(/* registration */) {
    console.log('Service worker has been registered.')
  },

  updated(registration) {
    console.log('New content is available; please refresh.')
    const mainStore = useMainStore()
    mainStore.registration = registration
    mainStore.showAppUpdatedBanner = true
  },

  updatefound(/* registration */) {
    console.log('New content is downloading.')
  },
})
