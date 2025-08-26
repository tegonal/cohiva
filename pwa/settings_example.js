/* Cohiva App settings */
const settings = {
  /* Settings similar to cohiva/base_config.py */
  PROD_HOSTNAME: "demo",
  TEST_HOSTNAME: "test.demo",
  DOMAIN: "cohiva.ch",
  SITE_NAME: "Genossenschaft Musterweg",
  SITE_NICKNAME: "Musterweg" /* App will be called "<SITE_NICKNAME>-App" */,
  APP_BASENAME: "musterweg",

  /* Additional settings */
  PASSWORD_RESET_LINK: "https://demo.cohiva.ch/portal/password_reset/",
  BUTTON_LINKS: {
    CHAT: {
      link: "https://chat.demo.cohiva.ch/",
    },
    CLOUD: {
      link: "https://cloud.demo.cohiva.ch/",
    },
    HANDBUCH: {
      link: "https://doku.demo.cohiva.ch/",
    },
  },
  NAVIGATION_LINKS: [
    {
      title: "Energieverbrauch",
      caption:
        "Strom und Energieverbrauch anzeigen (ein Login pro Mieteinheit)",
      icon: "electric_bolt",
      link: "https://web.egonline.ch/customer/login",
    },
    {
      title: "Cohiva Portal/Hilfe",
      caption: "demo.cohiva.ch",
      icon: "help_outline",
      link: "https://demo.cohova.ch/portal",
    },
    {
      title: "Cohiva Website",
      caption: "demo.cohiva.ch",
      icon: "public",
      link: "https://demo.cohiva.ch",
    },
  ],
  RESERVATION_LINKS: {
    NOTE: "",
    LINKS: [
      {
        title: "Infos Gästezimmer",
        caption: "Infos zur Nutzung der Gästezimmer",
        link: "https://demo.cohiva.ch/gaestezimmer/",
      },
      {
        title: "Kalender Bewegungsraum",
        caption: "Kalender für die Nutzung des Bewegungsraum",
        link: "https://demo.cohiva.ch/bewegungsraum_kalender/",
      },
    ],
  },
};

export { settings };
