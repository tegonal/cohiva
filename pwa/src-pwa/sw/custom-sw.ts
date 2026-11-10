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

declare const self: ServiceWorkerGlobalScope & typeof globalThis

void self.skipWaiting()
clientsClaim()

// Use with precache injection
precacheAndRoute(self.__WB_MANIFEST)

cleanupOutdatedCaches()

if (import.meta.env.QUASAR_PROD) {
  // Non-SSR/SSG fallbacks to index.html
  // Production SSR/SSG fallbacks to offline.html (except for dev)
  registerRoute(
    new NavigationRoute(
      createHandlerBoundToURL(import.meta.env.QUASAR_PWA_FALLBACK_HTML),
      {
        denylist: [
          new RegExp(import.meta.env.QUASAR_PWA_SERVICE_WORKER_REGEX),
          /workbox-(.)*\.js$/,
        ],
      }
    )
  )
}
