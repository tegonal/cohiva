/**
 * Add types for PWA-specific import.meta.env variables.
 * Quasar CLI v3+ uses import.meta.env instead of process.env.
 */
interface ImportMetaEnv {
  readonly QCLI_PWA_FALLBACK_HTML: string
  readonly QCLI_PWA_SERVICE_WORKER_REGEX: string
  readonly QCLI_SERVICE_WORKER_FILE: string
}
