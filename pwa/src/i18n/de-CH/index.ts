export default {
  // CalendarPage component translations
  calendarPage: {
    calendar: {
      allDay: 'Ganztags',
      day: 'Tag',
      list: 'Liste',
      month: 'Monat',
      noEvents: 'Keine Termine',
      today: 'Heute',
      week: 'Woche',
    },
    categories: {
      cooperative: 'Genossenschaft',
      guestRoom: 'Gästezimmer',
      plenary: 'Plena, GV etc.',
      reservation: 'Reservation',
    },
    errors: {
      calendarFeeds: 'Fehler beim Abrufen der CalendarFeeds.',
      general: 'Es ist ein Fehler aufgetreten.',
      missingCredentials: 'Anmeldedaten fehlen.',
    },
    filter: {
      all: 'Alle',
      label: 'Filter',
    },
    views: {
      day: 'Tag',
      list: 'Liste',
      month: 'Monat',
      weekOverview: 'Woche - Übersicht',
      weekTimeGrid: 'Woche - Zeitraster',
    },
    viewSelect: {
      label: 'Kalender-Ansicht',
    },
  },

  // CreditAccountingPage component translations
  creditAccountingPage: {
    account: 'Konto',
    csvExport: 'CSV Export',
    csvExportFilename: 'Depot8_Kontoauszug.csv',
    errors: {
      general: 'Es ist ein Fehler aufgetreten.',
      invalidToken: 'Ungültiges Token',
      missingCredentials: 'Anmeldedaten fehlen.',
    },
    filters: {
      allTransactions: 'Alle Buchungen',
      credits: 'Gutschriften',
      debits: 'Lastschriften',
    },
    messages: {
      displayed: 'angezeigt.',
      manyTransactions: 'Viele Buchungen gefunden. Es werden nur die neusten',
      noTransactions:
        'Keine Transaktionen gefunden. Allenfalls Filter oben anpassen.',
    },
    paymentDialog: {
      accountLabel: 'Konto',
      autoAssignment: 'automatisch dem richtigen Konto zugeordnet werden.',
      cancel: 'Abbrechen',
      depositText: 'einzuzahlen. So kann die Überweisung',
      instructions:
        'Bitte benutze den QR-Einzahlungsschein unten um Guthaben für dein Konto',
      qrSlip: 'QR-Einzahlungsschein (PDF)',
      title: 'Guthaben aufladen',
    },
    search: 'Suche',
    searchFilterLabel: 'Suche/Filter und weitere Funktionen',
    settings: 'Einstellungen',
    settingsDialog: {
      accountPrefix: 'Konto',
      cancel: 'Abbrechen',
      emailNotification: 'Email-Benachrichtigung,',
      emailTo: 'Email an',
      pinCode: 'PIN-Code',
      save: 'Speichern',
      warning: 'ACHTUNG: Betrifft alle Konto-Nutzer:innen',
      whenBalanceBelow: 'wenn Guthaben unter',
      withQrSlip: 'mit QR-Einzahlungsschein beim Unterschreiten dieser Limite.',
    },
    table: {
      amount: 'Betrag',
      balance: 'Saldo',
      date: 'Datum',
      description: 'Bezeichnung',
      note: 'Notiz',
    },
    timeRange: 'Zeitraum',
    title: 'Kontoauszug',
    type: 'Typ',
  },

  // IndexPage component translations
  indexPage: {
    buttons: {
      calendar: 'Kalender',
      chat: 'Chat',
      cloud: 'Cloud',
      depot8: 'Depot8',
      manual: 'Handbuch',
      repair: 'Reparaturmeldung',
      reservation: 'Reservation',
    },
    errors: {
      general: 'Es ist ein Fehler aufgetreten.',
      invalidToken: 'Ungültiges Token',
      missingCredentials: 'Anmeldedaten fehlen.',
    },
    messages: {
      testMode:
        'TESTMODUS - Änderungen werden lediglich an einen Testserver übermittelt.',
    },
  },

  // LoginPage component translations
  loginPage: {
    backendError: {
      retry: 'Erneut versuchen',
      title: 'Backend-Server nicht erreichbar',
    },
    checkingServer: 'Verbindung zum Server wird geprüft...',
    forgotPassword: 'Passwort vergessen?',
    loginButton: 'Mit {site} anmelden',
    loginError: 'Anmeldung fehlgeschlagen. Bitte versuche es erneut.',
    redirectNotice: 'Du wirst zur sicheren Anmeldeseite weitergeleitet.',
    title: 'Melde dich mit deinem {site}-Konto an:',
  },

  // MainLayout component translations
  mainLayout: {
    appVersion: {
      label: 'App-Version',
    },
    navigation: {
      links: 'Links',
      settings: 'Einstellungen',
    },
    user: {
      loggedInAs: 'Angemeldet als',
      logout: 'Abmelden',
      unknown: 'Unbekannt',
    },
  },

  // Page titles for SubpageLayout
  pageTitles: {
    calendar: 'Kalender',
    creditAccounting: 'Kontoauszug',
    repair: 'Reparaturmeldung',
    reservation: 'Reservation',
  },

  // RepairPage component translations
  repairPage: {
    errorDialog: {
      message: 'Die Meldung konnte nicht übermittelt werden.',
      ok: 'OK',
      reason: 'Grund:',
      title: 'Fehler',
    },
    errors: {
      general: 'Es ist ein Fehler aufgetreten.',
      saveFailed: 'Fehler beim Speichern.',
    },
    form: {
      affectedArea: {
        label: 'Betroffener Bereich/Bauteil',
      },
      affectedUnit: {
        label: 'Betroffene Wohnung/Raum',
        otherOption: 'Etwas anderes (bitte unter Betreff angeben)',
      },
      availability: {
        label: 'Erreichbarkeit',
        placeholder: 'Wann und wie bist du am besten erreichbar?',
      },
      description: {
        label: 'Beschreibung des Schadens',
        placeholder: 'Möglichst genaue Beschreibung des Schadens/Problems',
      },
      images: {
        label: 'Bilder hinzufügen',
      },
      requiredField: 'Pflichtfeld',
      subject: {
        label: 'Betreff',
        placeholder: 'Ein paar Stichworte um was es geht',
      },
      submitButton: 'Absenden',
    },
    notifications: {
      invalidFile: 'Ungültige Datei',
      maxImages: 'Es können max. 5 Bilder hinzugefügt werden.',
    },
    reportFrom: 'Meldung von:',
    successDialog: {
      message: 'Die Meldung wurde erfolgreich übermittelt.',
      ok: 'OK',
      title: 'Vielen Dank!',
    },
  },

  // ReservationEditPage component translations
  reservationEditPage: {
    close: 'Schliessen',
    confirmDialog: {
      cancelButton: 'Abbrechen',
      costs: 'Kosten:',
      date: 'Datum:',
      dateFrom: 'Von',
      dateTo: 'bis',
      defaultCost: ' Fr. 0.00',
      reason: {
        label: 'Anlass/Grund der Reservation',
        placeholder: 'Kurze Beschreibung',
        validation: 'Bitte Feld ausfüllen',
      },
      reserveButton: 'Reservieren',
      room: 'Raum:',
      title: 'Bitte bestätige deine Reservation:',
    },
    errorDialog: {
      message: 'Die Reservation konnte nicht abgeschlossen werden.',
      ok: 'OK',
      reason: 'Grund:',
      title: 'Fehler',
    },
    errors: {
      general: 'Es ist ein Fehler aufgetreten.',
      invalidToken: 'Ungültiges Token',
      missingCredentials: 'Anmeldedaten fehlen.',
      saveFailed: 'Fehler beim Speichern.',
    },
    from: 'Von',
    links: 'Links',
    noPermission:
      'Es gibt nichts, was du hier reservieren könntest. Möglicherweise fehlt dir die nötige Berechtigung.',
    notAvailable: 'Nicht verfügbar',
    note: 'Hinweis:',
    reserve: 'Reservieren',
    title: 'Neue Reservation',
    until: 'Bis',
    whatToReserve: 'Was möchtest du reservieren?',
  },

  // ReservationPage component translations
  reservationPage: {
    buttons: {
      edit: 'Editieren',
    },
    cancelDialog: {
      cancelButton: 'Nein, abbrechen',
      confirmButton: 'Ja, Stornieren!',
      date: 'Datum:',
      event: 'Anlass:',
      explanation:
        'Reservationen können momentan noch nicht geändert, sondern nur storniert werden. Danach kannst du eine neue Reservation erfassen.',
      question: 'Möchtest du die folgende Reservation definitiv stornieren?',
      room: 'Raum:',
      title: 'Reservation löschen?',
    },
    emptyState:
      'Du hast keine bevorstehenden Reservationen. Erstelle eine neue Reservation mit dem Plus-Knopf unten rechts.',
    errorDialog: {
      message: 'Die Reservation konnte nicht storniert werden.',
      ok: 'OK',
      reason: 'Grund:',
      title: 'Fehler',
    },
    errors: {
      general: 'Es ist ein Fehler aufgetreten.',
      invalidToken: 'Ungültiges Token',
      missingCredentials: 'Anmeldedaten fehlen.',
      saveFailed: 'Fehler beim Speichern.',
    },
    pastReservations: 'Vergangene Reservationen',
    status: {
      cancelled: 'STORNIERT',
    },
    title: 'Deine Reservationen',
  },
}
