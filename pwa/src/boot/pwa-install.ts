import '@khmyznikov/pwa-install'
import { defineBoot } from '#q-app'

// Register the PWA install web component globally
export default defineBoot(() => {
  // The import above registers the <pwa-install> custom element
  // No additional setup needed for basic usage
})
