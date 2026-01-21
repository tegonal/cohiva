import '@khmyznikov/pwa-install'
import { boot } from 'quasar/wrappers'

// Register the PWA install web component globally
export default boot(() => {
  // The import above registers the <pwa-install> custom element
  // No additional setup needed for basic usage
})
