const routes = [
  {
    path: "/",
    component: () => import("layouts/MainLayout.vue"),
    children: [
      { path: "", component: () => import("pages/IndexPage.vue") },
      {
        path: "login",
        name: "login",
        component: () => import("pages/LoginPage.vue"),
      },
    ],
  },
  {
    path: "/reservation",
    component: () => import("layouts/SubpageLayout.vue"),
    props: { subpageTitle: "Reservation" },
    children: [
      { path: "", component: () => import("pages/ReservationPage.vue") },
      {
        path: "add",
        component: () => import("pages/ReservationEditPage.vue"),
      },
    ],
  },
  {
    path: "/calendar",
    component: () => import("layouts/SubpageLayout.vue"),
    props: { subpageTitle: "Kalender" },
    children: [{ path: "", component: () => import("pages/CalendarPage.vue") }],
  },
  {
    path: "/repair",
    component: () => import("layouts/SubpageLayout.vue"),
    props: { subpageTitle: "Reparaturmeldung" },
    children: [{ path: "", component: () => import("pages/RepairPage.vue") }],
  },
  {
    path: "/credit_accounting",
    component: () => import("layouts/SubpageLayout.vue"),
    props: { subpageTitle: "Depot8" },
    children: [
      { path: "", component: () => import("pages/CreditAccountingPage.vue") },
    ],
  },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: "/:catchAll(.*)*",
    component: () => import("pages/ErrorNotFound.vue"),
  },
];

export default routes;
