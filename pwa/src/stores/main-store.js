import { defineStore } from "pinia";
import { version } from "../../package.json";

export const useMainStore = defineStore("main", {
  state: () => ({
    showAppUpdatedBanner: false,
    registration: null,
    appVersion: version,
    capabilities: { depot8: false, residentHo8: false },
  }),
  /*getters: {
    doubleCount: (state) => state.counter * 2,
  },*/
  actions: {
    update_version() {
      const prev_appVersion = JSON.parse(localStorage.getItem("appVersion"));
      if (prev_appVersion != this.appVersion) {
        localStorage.setItem("appVersion", JSON.stringify(this.appVersion));
        console.log(
          "Updated appVersion " + prev_appVersion + " -> " + this.appVersion
        );
      }
    },
    /*increment() {
      this.counter++;
    },*/
  },
});
