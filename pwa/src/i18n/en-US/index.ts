export default {
  // CalendarPage component translations
  calendarPage: {
    calendar: {
      allDay: 'All Day',
      day: 'Day',
      list: 'List',
      month: 'Month',
      noEvents: 'No Events',
      today: 'Today',
      week: 'Week',
    },
    categories: {
      cooperative: 'Cooperative',
      guestRoom: 'Guest Room',
      plenary: 'Plenary, GA etc.',
      reservation: 'Reservation',
    },
    errors: {
      calendarFeeds: 'Error retrieving calendar feeds.',
      general: 'An error occurred.',
      missingCredentials: 'Login credentials missing.',
    },
    filter: {
      all: 'All',
      label: 'Filter',
    },
    views: {
      day: 'Day',
      list: 'List',
      month: 'Month',
      weekOverview: 'Week - Overview',
      weekTimeGrid: 'Week - Time Grid',
    },
    viewSelect: {
      label: 'Calendar View',
    },
  },

  // CreditAccountingPage component translations
  creditAccountingPage: {
    account: 'Account',
    csvExport: 'CSV Export',
    csvExportFilename: 'Depot8_Account_Statement.csv',
    errors: {
      general: 'An error occurred.',
      invalidToken: 'Invalid Token',
      missingCredentials: 'Login credentials missing.',
    },
    filters: {
      allTransactions: 'All Transactions',
      credits: 'Credits',
      debits: 'Debits',
    },
    messages: {
      displayed: 'displayed.',
      manyTransactions: 'Many transactions found. Only the most recent',
      noTransactions:
        'No transactions found. Please adjust the filter above if necessary.',
    },
    paymentDialog: {
      accountLabel: 'Account',
      autoAssignment: 'automatically assigned to the correct account.',
      cancel: 'Cancel',
      depositText: 'to deposit. This way the transfer can be',
      instructions:
        'Please use the QR payment slip below to add credit to your account',
      qrSlip: 'QR Payment Slip (PDF)',
      title: 'Add Credit',
    },
    search: 'Search',
    searchFilterLabel: 'Search/Filter and additional functions',
    settings: 'Settings',
    settingsDialog: {
      accountPrefix: 'Account',
      cancel: 'Cancel',
      emailNotification: 'Email notification,',
      emailTo: 'Email to',
      pinCode: 'PIN Code',
      save: 'Save',
      warning: 'WARNING: Affects all account users',
      whenBalanceBelow: 'when balance below',
      withQrSlip: 'with QR payment slip when falling below this limit.',
    },
    table: {
      amount: 'Amount',
      balance: 'Balance',
      date: 'Date',
      description: 'Description',
      note: 'Note',
    },
    timeRange: 'Time Range',
    title: 'Account Statement',
    type: 'Type',
  },

  // IndexPage component translations
  indexPage: {
    buttons: {
      calendar: 'Calendar',
      chat: 'Chat',
      cloud: 'Cloud',
      depot8: 'Depot8',
      manual: 'Manual',
      repair: 'Repair Report',
      reservation: 'Reservation',
    },
    errors: {
      general: 'An error occurred.',
      invalidToken: 'Invalid Token',
      missingCredentials: 'Login credentials missing.',
    },
    messages: {
      testMode: 'TEST MODE - Changes are only sent to a test server.',
    },
  },

  // LoginPage component translations
  loginPage: {
    backendError: {
      retry: 'Try again',
      title: 'Backend server unreachable',
    },
    checkingServer: 'Checking server connection...',
    forgotPassword: 'Forgot password?',
    loginButton: 'Sign in with {site}',
    loginError: 'Login failed. Please try again.',
    redirectNotice: 'You will be redirected to the secure login page.',
    title: 'Sign in with your {site} account:',
  },

  // MainLayout component translations
  mainLayout: {
    appVersion: {
      label: 'App Version',
    },
    navigation: {
      links: 'Links',
      settings: 'Settings',
    },
    user: {
      loggedInAs: 'Logged in as',
      logout: 'Log out',
      unknown: 'Unknown',
    },
  },

  // Page titles for SubpageLayout
  pageTitles: {
    calendar: 'Calendar',
    creditAccounting: 'Account Statement',
    repair: 'Repair Report',
    reservation: 'Reservation',
  },

  // RepairPage component translations
  repairPage: {
    errorDialog: {
      message: 'The report could not be submitted.',
      ok: 'OK',
      reason: 'Reason:',
      title: 'Error',
    },
    errors: {
      general: 'An error occurred.',
      saveFailed: 'Error saving.',
    },
    form: {
      affectedArea: {
        label: 'Affected Area/Component',
      },
      affectedUnit: {
        label: 'Affected Apartment/Room',
        otherOption: 'Something else (please specify under subject)',
      },
      availability: {
        label: 'Availability',
        placeholder: 'When and how can you best be reached?',
      },
      description: {
        label: 'Damage Description',
        placeholder: 'Most detailed description of the damage/problem',
      },
      images: {
        label: 'Add Images',
      },
      requiredField: 'Required Field',
      subject: {
        label: 'Subject',
        placeholder: 'A few keywords about what this is about',
      },
      submitButton: 'Submit',
    },
    notifications: {
      invalidFile: 'Invalid File',
      maxImages: 'A maximum of 5 images can be added.',
    },
    reportFrom: 'Report from:',
    successDialog: {
      message: 'The report was successfully submitted.',
      ok: 'OK',
      title: 'Thank you!',
    },
  },

  // ReservationEditPage component translations
  reservationEditPage: {
    close: 'Close',
    confirmDialog: {
      cancelButton: 'Cancel',
      costs: 'Costs:',
      date: 'Date:',
      dateFrom: 'From',
      dateTo: 'to',
      defaultCost: ' CHF 0.00',
      reason: {
        label: 'Occasion/Reason for Reservation',
        placeholder: 'Brief description',
        validation: 'Please fill out this field',
      },
      reserveButton: 'Reserve',
      room: 'Room:',
      title: 'Please confirm your reservation:',
    },
    errorDialog: {
      message: 'The reservation could not be completed.',
      ok: 'OK',
      reason: 'Reason:',
      title: 'Error',
    },
    errors: {
      general: 'An error occurred.',
      invalidToken: 'Invalid Token',
      missingCredentials: 'Login credentials missing.',
      saveFailed: 'Error saving.',
    },
    from: 'From',
    links: 'Links',
    noPermission:
      'There is nothing you could reserve here. You may lack the necessary permissions.',
    notAvailable: 'Not Available',
    note: 'Note:',
    reserve: 'Reserve',
    title: 'New Reservation',
    until: 'Until',
    whatToReserve: 'What would you like to reserve?',
  },

  // ReservationPage component translations
  reservationPage: {
    buttons: {
      edit: 'Edit',
    },
    cancelDialog: {
      cancelButton: 'No, cancel',
      confirmButton: 'Yes, Cancel!',
      date: 'Date:',
      event: 'Event:',
      explanation:
        'Reservations cannot currently be modified, only cancelled. Afterwards you can create a new reservation.',
      question: 'Do you want to definitively cancel the following reservation?',
      room: 'Room:',
      title: 'Delete Reservation?',
    },
    emptyState:
      'You have no upcoming reservations. Create a new reservation with the plus button in the bottom right.',
    errorDialog: {
      message: 'The reservation could not be cancelled.',
      ok: 'OK',
      reason: 'Reason:',
      title: 'Error',
    },
    errors: {
      general: 'An error occurred.',
      invalidToken: 'Invalid Token',
      missingCredentials: 'Login credentials missing.',
      saveFailed: 'Error saving.',
    },
    pastReservations: 'Past Reservations',
    status: {
      cancelled: 'CANCELLED',
    },
    title: 'Your Reservations',
  },
}
