import { IdTokenClaims, User } from 'oidc-client-ts'
import { defineStore } from 'pinia'
import { Router } from 'vue-router'

import { settings } from 'app/config/settings'
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
          console.log('Backend health check: OK')
          return true
        } catch (fetchError: any) {
          clearTimeout(timeoutId)

          this.backendAvailable = false
          return false
        }
      } catch (error) {
        console.error('Backend health check error:', error)
        this.backendError = 'Fehler beim Prüfen der Backend-Verbindung'
        this.backendAvailable = false
        return false
      }
    },

    async clearStaleState(): Promise<void> {
      await oauthService.clearStaleState()
    },

    async getAccessToken(): Promise<null | string> {
      if (this.user && this.user.expired) {
        try {
          await this.refreshToken()
        } catch (error) {
          console.error('Failed to refresh token:', error)
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
        
        // Log the entire token contents for debugging
        console.log('=== OAuth User Object ===')
        console.log('Full user object:', user)
        console.log('Access token:', user.access_token)
        console.log('ID token:', user.id_token)
        console.log('Profile:', user.profile)
        console.log('Token type:', user.token_type)
        console.log('Scope:', user.scope)
        console.log('Expires at:', user.expires_at)
        
        // Decode and log ID token claims
        if (user.id_token) {
          try {
            const parts = user.id_token.split('.')
            if (parts[1]) {
              const payload = JSON.parse(window.atob(parts[1]))
              console.log('ID Token Claims:', payload)
            }
          } catch (e) {
            console.error('Failed to decode ID token:', e)
          }
        }
        console.log('=========================')
        
        // Optionally fetch fresh user info from the API
        // This demonstrates getting user data from the server instead of just the token
        try {
          const freshUserInfo = await this.fetchUserProfile()
          console.log('Fresh user info fetched successfully:', freshUserInfo)
        } catch (error) {
          console.error('Could not fetch fresh user info:', error)
          // Not critical - we already have user info from the token
        }
        
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
        console.error('Callback handling failed:', error)
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
      } catch (error) {
        console.error('Silent callback failed:', error)
      }
    },

    async initAuth(): Promise<void> {
      this.loading = true
      try {
        const user = await oauthService.getUser()
        if (user && !user.expired) {
          this.user = user
          
          // Log user info when loaded from storage
          console.log('=== User Loaded from Storage ===')
          console.log('Profile:', user.profile)
          console.log('Scopes:', user.scope)
          console.log('================================')
          
          oauthService.startSessionMonitor()
        } else if (user && user.expired) {
          await this.refreshToken()
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error)
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
        console.error('Login failed:', error)
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
      } catch (error) {
        console.error('Logout failed:', error)
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
        console.error('Token refresh failed:', error)
        this.error = error instanceof Error ? error.message : String(error)
        this.user = null
        throw error
      }
    },

    async fetchUserProfile(): Promise<any> {
      try {
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
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })

        if (!response.ok) {
          throw new Error(`Failed to fetch user info: ${response.status}`)
        }

        const userInfo = await response.json()
        console.log('=== Fresh User Info from API ===')
        console.log('UserInfo endpoint response:', userInfo)
        console.log('================================')
        
        // Update the user profile in the store if needed
        if (this.user) {
          this.user.profile = { ...this.user.profile, ...userInfo }
          console.log('Updated user profile:', this.user.profile)
        }
        
        return userInfo
      } catch (error) {
        console.error('Failed to fetch user profile:', error)
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
        console.log('User loaded in store:', user.profile.sub)
        this.user = user
      })

      oauthService.userManager.events.addUserUnloaded(() => {
        console.log('User unloaded in store')
        this.user = null
      })

      oauthService.userManager.events.addAccessTokenExpiring(() => {
        console.log('Token expiring, attempting refresh...')
      })

      oauthService.userManager.events.addAccessTokenExpired(() => {
        console.log('Token expired')
        this.user = null
      })

      oauthService.userManager.events.addSilentRenewError((error: Error) => {
        console.error('Silent renew error in store:', error)
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
