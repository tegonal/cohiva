/**
 * Add types for your custom import.meta.env variables.
 * Quasar CLI v3+ uses import.meta.env instead of process.env.
 */
interface ImportMetaEnv {
  readonly QCLI_API: string
  readonly QCLI_API_DIRECT: string
  readonly QCLI_OAUTH_CLIENT_ID: string
  readonly QCLI_TEST_MODE: string
}
