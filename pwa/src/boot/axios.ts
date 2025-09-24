import { defineBoot } from '#q-app/wrappers'
import { settings } from 'app/config/settings'
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

import { useAuthStore } from 'stores/auth-store'

interface ExtendedAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

// Determine API URL based on environment
// Both development and production use direct URLs since CORS is configured on backend
const isDevelopment = process.env.NODE_ENV === 'development'

const apiBaseURL = isDevelopment
  ? `https://${settings.testHostname}.${settings.domain}/`
  : `https://${settings.prodHostname}.${settings.domain}/`

const api = axios.create({
  baseURL: apiBaseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    if (config.url?.includes('/o/')) {
      return config
    }

    try {
      const authStore = useAuthStore()
      const token = await authStore.getAccessToken()

      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`
      }
    } catch (error) {
      console.error('Failed to get access token:', error)
    }

    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as ExtendedAxiosRequestConfig
    const authStore = useAuthStore()

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true

      try {
        await authStore.refreshToken()
        const token = await authStore.getAccessToken()

        if (token && originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError)
        authStore.logout()
        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  }
)

export default defineBoot(({ app }) => {
  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api
})

export { api }
