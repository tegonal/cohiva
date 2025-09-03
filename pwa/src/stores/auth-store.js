import { createSimpleExpression } from '@vue/compiler-core'
import { api } from 'boot/axios'
import { defineStore } from 'pinia'

//import { fetchWrapper, router } from "@/helpers";

function sleep(time) {
  return new Promise((resolve) => setTimeout(resolve, time))
}

export const useAuthStore = defineStore({
  actions: {
    async login(username, password) {
      //console.log("start request");
      //await sleep(4000);
      const response = await api.post('/dj-rest-auth/login/', {
        email: username.value,
        password: password.value,
      })

      //console.log(response);
      //console.log("login response: " + response.data.key);
      this.token = response.data.key
      const user = username.value

      // update pinia state
      this.user = user

      // store user details and jwt in local storage to keep user logged in between page refreshes
      localStorage.setItem('user', JSON.stringify(this.user))
      localStorage.setItem('token', JSON.stringify(this.token))

      // redirect to previous url or default to home page
      console.log('Login: Push returnUrl to router')
      this.router.push(this.returnUrl || '/')
    },
    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
      console.log('Logout')
      this.router.push('/login')
    },
  },
  id: 'auth',
  state: () => ({
    returnUrl: null,
    token: JSON.parse(localStorage.getItem('token')),
    // initialize state from local storage to enable user to stay logged in
    user: JSON.parse(localStorage.getItem('user')),
  }),
})
