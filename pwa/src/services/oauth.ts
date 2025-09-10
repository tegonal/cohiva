import { settings } from 'app/config/settings'
import {
  OidcMetadata,
  User,
  UserManager,
  UserManagerSettings,
  WebStorageStateStore,
} from 'oidc-client-ts'

interface ExtraLoginParams {
  login_hint?: string
  prompt?: string
  state?: OAuthState
}

interface OAuthState {
  returnUrl?: string
}

const createOAuthSettings = (): UserManagerSettings => {
  // Determine API URL based on environment
  const isDevelopment = process.env.NODE_ENV === 'development'
  const baseUrl = isDevelopment
    ? `https://${settings.TEST_HOSTNAME}.${settings.DOMAIN}`
    : `https://${settings.PROD_HOSTNAME}.${settings.DOMAIN}`

  const appUrl = window.location.origin

  if (!settings.OAUTH_CLIENT_ID) {
    throw new Error('OAUTH_CLIENT_ID is required in settings')
  }

  return {
    authority: baseUrl,
    automaticSilentRenew: true,
    checkSessionIntervalInSeconds: 30,
    client_id: settings.OAUTH_CLIENT_ID,
    filterProtocolClaims: true,
    loadUserInfo: true,
    metadata: {
      authorization_endpoint: `${baseUrl}/o/authorize/`,
      end_session_endpoint: `${baseUrl}/o/logout/`,
      issuer: baseUrl,
      revocation_endpoint: `${baseUrl}/o/revoke_token/`,
      token_endpoint: `${baseUrl}/o/token/`,
      userinfo_endpoint: `${baseUrl}/o/userinfo/`,
    } as OidcMetadata,
    metadataUrl: `${baseUrl}/o/.well-known/openid-configuration`,
    monitorSession: true,
    post_logout_redirect_uri: `${appUrl}/`,
    redirect_uri: `${appUrl}/auth/callback`,
    requestTimeoutInSeconds: 30,
    response_type: 'code',
    revokeTokensOnSignout: true,
    scope: 'openid read write profile username email',
    silent_redirect_uri: `${appUrl}/auth/silent-renew`,
    userStore: new WebStorageStateStore({
      store: window.sessionStorage,
    }),
    // PKCE is enabled by default, no client_secret for public client
    // disablePKCE: false, // Keep PKCE enabled (default)
  }
}

class OAuthService {
  public userManager: null | UserManager = null

  constructor() {
    this.initializeUserManager()
  }

  async clearStaleState(): Promise<void> {
    if (!this.userManager) return
    await this.userManager.clearStaleState()
  }

  async getAccessToken(): Promise<null | string> {
    const user = await this.getUser()
    return user?.access_token || null
  }

  async getUser(): Promise<null | User> {
    if (!this.userManager) return null
    try {
      const user = await this.userManager.getUser()
      return user
    } catch (error) {
      console.error('Failed to get user:', error)
      return null
    }
  }

  async handleCallback(): Promise<User> {
    if (!this.userManager) {
      throw new Error('UserManager not initialized')
    }
    try {
      const user = await this.userManager.signinRedirectCallback()
      return user
    } catch (error) {
      console.error('Callback handling failed:', error)
      throw error
    }
  }

  async handleSilentCallback(): Promise<void> {
    if (!this.userManager) return
    try {
      await this.userManager.signinSilentCallback()
    } catch (error) {
      console.error('Silent callback failed:', error)
    }
  }

  initializeUserManager(): void {
    try {
      const settings = createOAuthSettings()
      this.userManager = new UserManager(settings)

      this.userManager.events.addUserLoaded(() => {
        // User loaded event
      })

      this.userManager.events.addUserUnloaded(() => {
        // User unloaded event
      })

      this.userManager.events.addAccessTokenExpiring(() => {
        // Token expiring event
      })

      this.userManager.events.addAccessTokenExpired(() => {
        // Token expired event
      })

      this.userManager.events.addSilentRenewError((error: Error) => {
        console.error('Silent renew error:', error)
      })

      this.userManager.events.addUserSignedOut(() => {
        // User signed out event
      })
    } catch (error) {
      console.error('Failed to initialize UserManager:', error)
    }
  }

  async isAuthenticated(): Promise<boolean> {
    const user = await this.getUser()
    return !!user && !user.expired
  }

  async login(extraParams: ExtraLoginParams = {}): Promise<void> {
    if (!this.userManager) {
      throw new Error('UserManager not initialized')
    }
    try {
      await this.userManager.signinRedirect({
        state: {
          returnUrl: window.location.pathname,
        } as OAuthState,
        ...extraParams,
      })
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  async logout(): Promise<void> {
    if (!this.userManager) return
    try {
      await this.userManager.signoutRedirect()
    } catch (error) {
      console.error('Logout failed:', error)
      await this.userManager.removeUser()
      window.location.href = '/'
    }
  }

  async refreshToken(): Promise<User> {
    if (!this.userManager) {
      throw new Error('UserManager not initialized')
    }
    try {
      const user = await this.userManager.signinSilent()
      if (!user) {
        throw new Error('Failed to refresh token: no user returned')
      }
      return user
    } catch (error) {
      console.error('Token refresh failed:', error)
      throw error
    }
  }

  startSessionMonitor(): void {
    if (!this.userManager) return
    if (this.userManager.settings.monitorSession) {
      this.userManager.startSilentRenew()
    }
  }

  stopSessionMonitor(): void {
    if (!this.userManager) return
    this.userManager.stopSilentRenew()
  }
}

export const oauthService = new OAuthService()
export const oauthEvents = oauthService.userManager?.events
export default oauthService
