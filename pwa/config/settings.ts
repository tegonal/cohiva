/* Cohiva App settings - Default Configuration */

import type { Settings } from './schemas'

const settings: Settings = {
  appBasename: 'cohiva',
  buttonLinks: {
    chat: {
      link: 'https://chat.demo.cohiva.ch/',
    },
    cloud: {
      link: 'https://cloud.demo.cohiva.ch/',
    },
    handbuch: {
      link: 'https://doku.demo.cohiva.ch/',
    },
  },
  domain: 'cohiva.ch',
  navigationLinks: [
    {
      caption:
        'Strom und Energieverbrauch anzeigen (ein Login pro Mieteinheit)',
      icon: 'electric_bolt',
      link: 'https://web.egonline.ch/customer/login',
      title: 'Energieverbrauch',
    },
    {
      caption: 'demo.cohiva.ch',
      icon: 'help_outline',
      link: 'https://demo.cohiva.ch/portal',
      title: 'Cohiva Portal/Hilfe',
    },
    {
      caption: 'demo.cohiva.ch',
      icon: 'public',
      link: 'https://demo.cohiva.ch',
      title: 'Cohiva Website',
    },
  ],
  // OAuth2 Public Client Configuration (PKCE flow - no secret needed)
  oauthClientId: 'rVMu5eTlkLDkXFtbzuQ7bhhi5QgPlPXHb0bKkQf1',
  /* Additional settings */
  passwordResetLink: 'https://demo.cohiva.ch/portal/password_reset/',
  /* Settings similar to cohiva/base_config.py */
  prodHostname: 'demo',

  reservationLinks: {
    links: [
      {
        caption: 'Infos zur Nutzung der Gästezimmer',
        link: 'https://demo.cohiva.ch/gaestezimmer/',
        title: 'Infos Gästezimmer',
      },
      {
        caption: 'Kalender für die Nutzung des Bewegungsraum',
        link: 'https://demo.cohiva.ch/bewegungsraum_kalender/',
        title: 'Kalender Bewegungsraum',
      },
    ],
    note: '',
  },
  // Note: Client must be configured as 'public' in Django OAuth Toolkit
  // with PKCE enabled for security

  siteDescription: 'Cohiva Demo - Verwaltung für Wohngenossenschaften',
  siteName: 'Cohiva Demo',
  siteNickname: 'Cohiva',
  // Skip icon trimming during icon generation (useful for logos that need to preserve aspect ratio)
  // Set to true if your logo appears cut off or doesn't look good after Icon Genie processing
  skipIconTrim: false,
  testHostname: 'demo',
}

export { settings, type Settings }
