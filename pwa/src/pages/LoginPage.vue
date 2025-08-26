<template>
  <q-page>
    <div class="flex flex-center">
      <img
        :alt="settings.SITE_NICKNAME + ' Logo'"
        src="~assets/logo.svg"
        style="width: 200px; height: 200px"
      />
    </div>
    <div class="row flex-center q-px-md">
      <div class="col-xs-12 col-sm-8 col-md-6 col-lg-4 text-center">
        <h6>Melde dich mit deinem {{ settings.SITE_NICKNAME }}-Konto an:</h6>
        <div class="row">
          <q-input
            v-model="email"
            outlined
            type="email"
            :rules="[
              (val, rules) =>
                rules.email(val) || 'Bitte gib eine gültige Email-Adresse ein',
            ]"
            label="Email-Adresse"
            class="full-width q-my-xs"
            :autofocus="email.length == 0"
          >
            <template v-slot:prepend>
              <q-icon name="alternate_email" />
            </template>
          </q-input>
          <q-input
            v-model="password"
            outlined
            type="password"
            :rules="[(val) => !!val || 'Bitte gib ein Passwort ein']"
            label="Passwort"
            class="full-width q-mb-md"
            @keyup.enter="login()"
            :autofocus="email.length != 0"
          >
            <template v-slot:prepend>
              <q-icon name="lock" />
            </template>
          </q-input>
          <q-btn
            color="primary"
            class="full-width q-my-xs"
            @click="login()"
            :disabled="isSubmitting || !password || !email"
            ><q-spinner
              v-if="isSubmitting"
              color="secondary"
              size="1em"
              class="q-pa-xs"
            />Anmelden</q-btn
          >
          <div
            v-if="apiError"
            class="q-mt-md text-subtitle-1 text-negative text-center full-width"
          >
            <div>
              <q-icon name="warning" size="2em" />
            </div>
            <div>{{ apiError }}</div>
          </div>
          <p class="q-mt-lg text-center full-width text-grey-6 text-subtitle-1">
            <a :href="settings.PASSWORD_RESET_LINK">Passwort vergessen?</a>
          </p>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from "vue";
import { useAuthStore } from "stores";
import { settings } from "app/settings.js";

const email = ref(JSON.parse(localStorage.getItem("user")) || "");
const password = ref("");
const apiError = ref("");
const isSubmitting = ref(false);

function login() {
  const authStore = useAuthStore();
  apiError.value = "";
  isSubmitting.value = true;
  const response = authStore
    .login(email, password)
    .then((response) => {
      //console.log("Got result: " + response);
      isSubmitting.value = false;
    })
    .catch((error) => {
      isSubmitting.value = false;
      console.log("ERROR: " + error);
      apiError.value = "Fehler beim Anmelden";
    });
  //;
  //console.log("After login request");
  /* if (response) {

    apiError.value = response.value;
  }*/
  //return authStore.login(email, password).catch((error) => console.log(error));
}
</script>
