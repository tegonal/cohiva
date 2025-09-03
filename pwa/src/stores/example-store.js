import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', {
  actions: {
    increment() {
      this.counter++
    },
  },
  getters: {
    doubleCount: (state) => state.counter * 2,
  },
  state: () => ({
    counter: 0,
  }),
})
