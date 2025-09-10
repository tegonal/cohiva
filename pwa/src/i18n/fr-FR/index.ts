export default {
  // CalendarPage component translations
  calendarPage: {
    calendar: {
      allDay: 'Toute la journée',
      day: 'Jour',
      list: 'Liste',
      month: 'Mois',
      noEvents: 'Aucun événement',
      today: "Aujourd'hui",
      week: 'Semaine',
    },
    categories: {
      cooperative: 'Coopérative',
      guestRoom: "Chambre d'hôtes",
      plenary: 'Plénière, AG etc.',
      reservation: 'Réservation',
    },
    errors: {
      calendarFeeds: 'Erreur lors de la récupération des flux de calendrier.',
      general: "Une erreur s'est produite.",
      missingCredentials: 'Données de connexion manquantes.',
    },
    filter: {
      all: 'Tous',
      label: 'Filtre',
    },
    views: {
      day: 'Jour',
      list: 'Liste',
      month: 'Mois',
      weekOverview: "Semaine - Vue d'ensemble",
      weekTimeGrid: 'Semaine - Grille horaire',
    },
    viewSelect: {
      label: 'Vue du calendrier',
    },
  },

  // CreditAccountingPage component translations
  creditAccountingPage: {
    account: 'Compte',
    csvExport: 'Export CSV',
    csvExportFilename: 'Depot8_Releve_de_compte.csv',
    errors: {
      general: "Une erreur s'est produite.",
      invalidToken: 'Jeton invalide',
      missingCredentials: 'Données de connexion manquantes.',
    },
    filters: {
      allTransactions: 'Toutes les transactions',
      credits: 'Crédits',
      debits: 'Débits',
    },
    messages: {
      displayed: 'affichées.',
      manyTransactions:
        'Nombreuses transactions trouvées. Seules les plus récentes sont',
      noTransactions:
        'Aucune transaction trouvée. Veuillez éventuellement ajuster le filtre ci-dessus.',
    },
    paymentDialog: {
      accountLabel: 'Compte',
      autoAssignment: 'automatiquement attribuée au bon compte.',
      cancel: 'Annuler',
      depositText: 'à déposer. Ainsi, le virement peut être',
      instructions:
        'Veuillez utiliser le bulletin de versement QR ci-dessous pour ajouter du crédit à votre compte',
      qrSlip: 'Bulletin de versement QR (PDF)',
      title: 'Recharger le crédit',
    },
    search: 'Recherche',
    searchFilterLabel: 'Recherche/Filtre et fonctions supplémentaires',
    settings: 'Paramètres',
    settingsDialog: {
      accountPrefix: 'Compte',
      cancel: 'Annuler',
      emailNotification: 'Notification par e-mail,',
      emailTo: 'E-mail à',
      pinCode: 'Code PIN',
      save: 'Enregistrer',
      warning: 'ATTENTION : Concerne tous les utilisateurs du compte',
      whenBalanceBelow: 'quand le solde est inférieur à',
      withQrSlip:
        'avec bulletin de versement QR en cas de dépassement de cette limite.',
    },
    table: {
      amount: 'Montant',
      balance: 'Solde',
      date: 'Date',
      description: 'Désignation',
      note: 'Note',
    },
    timeRange: 'Période',
    title: 'Relevé de compte',
    type: 'Type',
  },

  // IndexPage component translations
  indexPage: {
    buttons: {
      calendar: 'Calendrier',
      chat: 'Chat',
      cloud: 'Cloud',
      depot8: 'Depot8',
      manual: 'Manuel',
      repair: 'Signalement de réparation',
      reservation: 'Réservation',
    },
    errors: {
      general: "Une erreur s'est produite.",
      invalidToken: 'Jeton invalide',
      missingCredentials: 'Données de connexion manquantes.',
    },
    messages: {
      testMode:
        'MODE TEST - Les modifications sont uniquement transmises à un serveur de test.',
    },
  },

  // LoginPage component translations
  loginPage: {
    backendError: {
      retry: 'Réessayer',
      title: 'Serveur backend inaccessible',
    },
    checkingServer: 'Vérification de la connexion au serveur...',
    forgotPassword: 'Mot de passe oublié ?',
    loginButton: 'Se connecter avec {site}',
    loginError: 'Échec de la connexion. Veuillez réessayer.',
    redirectNotice: 'Vous serez redirigé vers la page de connexion sécurisée.',
    title: 'Connectez-vous avec votre compte {site} :',
  },

  // MainLayout component translations
  mainLayout: {
    appVersion: {
      label: "Version de l'application",
    },
    navigation: {
      links: 'Liens',
      settings: 'Paramètres',
    },
    user: {
      loggedInAs: 'Connecté en tant que',
      logout: 'Se déconnecter',
      unknown: 'Inconnu',
    },
  },

  // RepairPage component translations
  repairPage: {
    errorDialog: {
      message: "Le signalement n'a pas pu être transmis.",
      ok: 'OK',
      reason: 'Raison :',
      title: 'Erreur',
    },
    errors: {
      general: "Une erreur s'est produite.",
      saveFailed: "Erreur lors de l'enregistrement.",
    },
    form: {
      affectedArea: {
        label: 'Zone/Composant affecté',
      },
      affectedUnit: {
        label: 'Appartement/Pièce affecté(e)',
        otherOption: 'Autre chose (veuillez préciser sous objet)',
      },
      availability: {
        label: 'Disponibilité',
        placeholder: 'Quand et comment peut-on vous joindre au mieux ?',
      },
      description: {
        label: 'Description du dommage',
        placeholder: 'Description la plus précise possible du dommage/problème',
      },
      images: {
        label: 'Ajouter des images',
      },
      requiredField: 'Champ obligatoire',
      subject: {
        label: 'Objet',
        placeholder: 'Quelques mots-clés sur le sujet',
      },
      submitButton: 'Envoyer',
    },
    notifications: {
      invalidFile: 'Fichier invalide',
      maxImages: 'Un maximum de 5 images peut être ajouté.',
    },
    reportFrom: 'Signalement de :',
    successDialog: {
      message: 'Le signalement a été transmis avec succès.',
      ok: 'OK',
      title: 'Merci !',
    },
  },

  // ReservationEditPage component translations
  reservationEditPage: {
    close: 'Fermer',
    confirmDialog: {
      cancelButton: 'Annuler',
      costs: 'Coûts :',
      date: 'Date :',
      dateFrom: 'De',
      dateTo: 'à',
      defaultCost: ' CHF 0.00',
      reason: {
        label: 'Occasion/Raison de la réservation',
        placeholder: 'Brève description',
        validation: 'Veuillez remplir ce champ',
      },
      reserveButton: 'Réserver',
      room: 'Pièce :',
      title: 'Veuillez confirmer votre réservation :',
    },
    errorDialog: {
      message: "La réservation n'a pas pu être finalisée.",
      ok: 'OK',
      reason: 'Raison :',
      title: 'Erreur',
    },
    errors: {
      general: "Une erreur s'est produite.",
      invalidToken: 'Jeton invalide',
      missingCredentials: 'Données de connexion manquantes.',
      saveFailed: "Erreur lors de l'enregistrement.",
    },
    from: 'De',
    links: 'Liens',
    noPermission:
      "Il n'y a rien que vous puissiez réserver ici. Il vous manque peut-être les autorisations nécessaires.",
    notAvailable: 'Non disponible',
    note: 'Remarque :',
    reserve: 'Réserver',
    title: 'Nouvelle réservation',
    until: "Jusqu'à",
    whatToReserve: 'Que souhaitez-vous réserver ?',
  },

  // ReservationPage component translations
  reservationPage: {
    buttons: {
      edit: 'Modifier',
    },
    cancelDialog: {
      cancelButton: 'Non, annuler',
      confirmButton: 'Oui, annuler !',
      date: 'Date :',
      event: 'Occasion :',
      explanation:
        'Les réservations ne peuvent actuellement pas être modifiées, seulement annulées. Vous pourrez ensuite créer une nouvelle réservation.',
      question: 'Voulez-vous définitivement annuler la réservation suivante ?',
      room: 'Pièce :',
      title: 'Supprimer la réservation ?',
    },
    emptyState:
      "Vous n'avez aucune réservation à venir. Créez une nouvelle réservation avec le bouton plus en bas à droite.",
    errorDialog: {
      message: "La réservation n'a pas pu être annulée.",
      ok: 'OK',
      reason: 'Raison :',
      title: 'Erreur',
    },
    errors: {
      general: "Une erreur s'est produite.",
      invalidToken: 'Jeton invalide',
      missingCredentials: 'Données de connexion manquantes.',
      saveFailed: "Erreur lors de l'enregistrement.",
    },
    pastReservations: 'Réservations passées',
    status: {
      cancelled: 'ANNULÉE',
    },
    title: 'Vos réservations',
  },
}
