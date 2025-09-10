/* Cohiva App settings - Default Configuration */

import type { Settings } from './schemas'

const settings: Settings = {
  APP_BASENAME: 'cohiva',
  BUTTON_LINKS: {
    CHAT: {
      link: 'https://chat.demo.cohiva.ch/',
    },
    CLOUD: {
      link: 'https://cloud.demo.cohiva.ch/',
    },
    HANDBUCH: {
      link: 'https://doku.demo.cohiva.ch/',
    },
  },
  DOMAIN: 'cohiva.ch',
  NAVIGATION_LINKS: [
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
  OAUTH_CLIENT_ID: 'rVMu5eTlkLDkXFtbzuQ7bhhi5QgPlPXHb0bKkQf1',
  /* Additional settings */
  PASSWORD_RESET_LINK: 'https://demo.cohiva.ch/portal/password_reset/',
  /* Settings similar to cohiva/base_config.py */
  PROD_HOSTNAME: 'demo',

  RESERVATION_LINKS: {
    LINKS: [
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
    NOTE: '',
  },
  // Note: Client must be configured as 'public' in Django OAuth Toolkit
  // with PKCE enabled for security

  SITE_DESCRIPTION: 'Cohiva Demo - Verwaltung für Wohngenossenschaften',
  SITE_NAME: 'Cohiva Demo',
  SITE_NICKNAME: 'Cohiva',
  TEST_HOSTNAME: 'demo',
}

export { settings, type Settings }
