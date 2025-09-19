import { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    children: [
      { component: () => import('pages/IndexPage.vue'), path: '' },
      {
        component: () => import('pages/LoginPage.vue'),
        name: 'login',
        path: 'login',
      },
      {
        component: () => import('pages/AuthCallback.vue'),
        name: 'auth-callback',
        path: 'auth/callback',
      },
      {
        component: () => import('pages/AuthSilentRenew.vue'),
        name: 'auth-silent-renew',
        path: 'auth/silent-renew',
      },
    ],
    component: () => import('layouts/MainLayout.vue'),
    path: '/',
  },
  {
    children: [
      { component: () => import('pages/ReservationPage.vue'), path: '' },
      {
        component: () => import('pages/ReservationEditPage.vue'),
        path: 'add',
      },
    ],
    component: () => import('layouts/SubpageLayout.vue'),
    path: '/reservation',
    props: { subpageTitle: 'Reservation' },
  },
  {
    children: [{ component: () => import('pages/CalendarPage.vue'), path: '' }],
    component: () => import('layouts/SubpageLayout.vue'),
    path: '/calendar',
    props: { subpageTitle: 'Kalender' },
  },
  {
    children: [{ component: () => import('pages/RepairPage.vue'), path: '' }],
    component: () => import('layouts/SubpageLayout.vue'),
    path: '/repair',
    props: { subpageTitle: 'Reparaturmeldung' },
  },
  {
    children: [
      { component: () => import('pages/CreditAccountingPage.vue'), path: '' },
    ],
    component: () => import('layouts/SubpageLayout.vue'),
    path: '/credit_accounting',
    props: { subpageTitle: 'Depot8' },
  },
  {
    component: () => import('pages/ErrorNotFound.vue'),
    path: '/:catchAll(.*)*',
  },
]

export default routes
