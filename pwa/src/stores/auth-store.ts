import { settings } from 'app/config/settings'
import { IdTokenClaims, User } from 'oidc-client-ts'
import { defineStore } from 'pinia'
import { Router } from 'vue-router'

import oauthService from 'src/services/oauth'

interface AuthState {
  backendAvailable: boolean
  backendError: null | string
  error: null | string
  loading: boolean
  returnUrl: null | string
  user: null | User
}

interface OAuthStateData {
  returnUrl?: string
}

interface UserProfile extends IdTokenClaims {
  [key: string]: unknown
  email?: string
  preferred_username?: string
}

export const useAuthStore = defineStore('auth', {
  actions: {
    async checkAuth(): Promise<boolean> {
      const isAuth = await oauthService.isAuthenticated()
      if (!isAuth) {
        this.user = null
      }
      return isAuth
    },

    async checkBackendHealth(): Promise<boolean> {
      this.backendError = null

      try {
        // Get the backend URL from settings
        const isDevelopment = process.env.NODE_ENV === 'development'
        const baseUrl = isDevelopment
          ? `https://${(await import('app/config/settings')).settings.TEST_HOSTNAME}.${(await import('app/config/settings')).settings.DOMAIN}`
          : `https://${(await import('app/config/settings')).settings.PROD_HOSTNAME}.${(await import('app/config/settings')).settings.DOMAIN}`

        // Create an AbortController for timeout
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 10000) // 10 second timeout

        try {
          await fetch(`${baseUrl}`, {
            method: 'HEAD',
            mode: 'no-cors', // Use no-cors to avoid CORS issues, we just want to know if it's reachable
            signal: controller.signal,
          })

          clearTimeout(timeoutId)

          // In no-cors mode, we can't read the response but if it doesn't throw, the server is reachable
          this.backendAvailable = true
          return true
        } catch {
          clearTimeout(timeoutId)

          this.backendAvailable = false
          return false
        }
      } catch {
        this.backendError = 'Fehler beim Prüfen der Backend-Verbindung'
        this.backendAvailable = false
        return false
      }
    },

    async clearStaleState(): Promise<void> {
      await oauthService.clearStaleState()
    },

    async fetchUserProfile(): Promise<any> {
      // Option 1: Use the OIDC userinfo endpoint directly
      const token = await this.getAccessToken()
      if (!token) {
        throw new Error('No access token available')
      }

      const isDevelopment = process.env.NODE_ENV === 'development'
      const baseUrl = isDevelopment
        ? `https://${settings.TEST_HOSTNAME}.${settings.DOMAIN}`
        : `https://${settings.PROD_HOSTNAME}.${settings.DOMAIN}`

      const response = await fetch(`${baseUrl}/o/userinfo/`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch user info: ${response.status}`)
      }

      const userInfo = await response.json()

      if (this.user) {
        this.user.profile = { ...this.user.profile, ...userInfo }
      }

      return userInfo
    },

    async getAccessToken(): Promise<null | string> {
      if (this.user && this.user.expired) {
        try {
          await this.refreshToken()
        } catch {
          return null
        }
      }
      return this.user?.access_token || null
    },

    async handleCallback(router: Router): Promise<undefined | User> {
      this.loading = true
      this.error = null

      try {
        const user = await oauthService.handleCallback()
        this.user = user

        oauthService.startSessionMonitor()

        const state = user?.state as OAuthStateData | undefined
        const returnUrl =
          state?.returnUrl || sessionStorage.getItem('auth_return_url') || '/'

        sessionStorage.removeItem('auth_return_url')

        if (router) {
          router.push(returnUrl)
        }

        return user
      } catch (error) {
        this.error = error instanceof Error ? error.message : String(error)
        if (router) {
          router.push('/login')
        }
        throw error
      } finally {
        this.loading = false
      }
    },

    async handleSilentCallback(): Promise<void> {
      try {
        await oauthService.handleSilentCallback()
      } catch {
        // Silent callback errors are handled in the service
      }
    },

    async initAuth(): Promise<void> {
      this.loading = true
      try {
        const user = await oauthService.getUser()
        if (user && !user.expired) {
          this.user = user
          oauthService.startSessionMonitor()
        } else if (user && user.expired) {
          await this.refreshToken()
        }
      } catch (error) {
        this.error = error instanceof Error ? error.message : String(error)
      } finally {
        this.loading = false
      }
    },

    async login(returnUrl: null | string = null): Promise<void> {
      this.loading = true
      this.error = null
      this.returnUrl = returnUrl

      try {
        if (returnUrl) {
          sessionStorage.setItem('auth_return_url', returnUrl)
        }

        await oauthService.login({
          state: { returnUrl: returnUrl || '/' },
        })
      } catch (error) {
        this.error = error instanceof Error ? error.message : String(error)
        this.loading = false
      }
    },

    async logout(): Promise<void> {
      this.loading = true

      try {
        oauthService.stopSessionMonitor()
        this.user = null
        this.error = null
        this.returnUrl = null
        await oauthService.logout()
      } catch {
        this.user = null
        window.location.href = '/'
      } finally {
        this.loading = false
      }
    },

    async refreshToken(): Promise<User> {
      try {
        const user = await oauthService.refreshToken()
        this.user = user
        return user
      } catch (error) {
        this.error = error instanceof Error ? error.message : String(error)
        this.user = null
        throw error
      }
    },

    setReturnUrl(url: string): void {
      this.returnUrl = url
      sessionStorage.setItem('auth_return_url', url)
    },

    setupEventListeners(): void {
      if (!oauthService.userManager) return

      oauthService.userManager.events.addUserLoaded((user: User) => {
        this.user = user
      })

      oauthService.userManager.events.addUserUnloaded(() => {
        this.user = null
      })

      oauthService.userManager.events.addAccessTokenExpiring(() => {
        // Token expiring - auto-refresh will handle it
      })

      oauthService.userManager.events.addAccessTokenExpired(() => {
        this.user = null
      })

      oauthService.userManager.events.addSilentRenewError(() => {
        this.error = 'Session refresh failed. Please login again.'
      })
    },
  },

  getters: {
    accessToken: (state): null | string => state.user?.access_token || null,
    idToken: (state): null | string => state.user?.id_token || null,
    isAuthenticated: (state): boolean => !!state.user && !state.user.expired,
    userEmail: (state): null | string => {
      const profile = state.user?.profile as undefined | UserProfile
      return profile?.email || null
    },
    username: (state): null | string => {
      const profile = state.user?.profile as undefined | UserProfile
      return profile?.preferred_username || profile?.email || null
    },
    userProfile: (state): null | UserProfile => {
      return (state.user?.profile as UserProfile) || null
    },
  },

  state: (): AuthState => ({
    backendAvailable: true, // Assume available initially
    backendError: null,
    error: null,
    loading: false,
    returnUrl: null,
    user: null,
  }),
})
