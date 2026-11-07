declare const self: ServiceWorkerGlobalScope &
  typeof globalThis & { skipWaiting: () => void }

/*
 * This file (which will be your service worker)
 * is picked up by the build system ONLY if
 * quasar.config.ts > pwa > workboxMode is set to "injectManifest"
 */

import { clientsClaim } from 'workbox-core'
import {
  cleanupOutdatedCaches,
  createHandlerBoundToURL,
  precacheAndRoute,
} from 'workbox-precaching'
import { NavigationRoute, registerRoute } from 'workbox-routing'

self.skipWaiting()
clientsClaim()

// Use with precache injection
precacheAndRoute(self.__WB_MANIFEST)

cleanupOutdatedCaches()

// Non-SSR fallback to index.html
// Production SSR fallback to offline.html (except for dev)
if (import.meta.env.QUASAR_MODE !== 'ssr' || import.meta.env.QUASAR_PROD) {
  registerRoute(
    new NavigationRoute(
      createHandlerBoundToURL(import.meta.env.QUASAR_PWA_FALLBACK_HTML),
      { denylist: [/sw\.js$/, /workbox-(.)*\.js$/] }
    )
  )
}
