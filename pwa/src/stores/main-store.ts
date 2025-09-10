import { defineStore } from 'pinia'

import { version } from '../../package.json'

interface Capabilities {
  depot8: boolean
  residentHo8: boolean
}

interface MainState {
  appVersion: string
  capabilities: Capabilities
  registration: null | ServiceWorkerRegistration
  showAppUpdatedBanner: boolean
}

export const useMainStore = defineStore('main', {
  actions: {
    update_version(): void {
      const prev_appVersion = JSON.parse(
        localStorage.getItem('appVersion') || 'null'
      )
      if (prev_appVersion !== this.appVersion) {
        localStorage.setItem('appVersion', JSON.stringify(this.appVersion))
      }
    },
  },

  state: (): MainState => ({
    appVersion: version,
    capabilities: { depot8: false, residentHo8: false },
    registration: null,
    showAppUpdatedBanner: false,
  }),
})
