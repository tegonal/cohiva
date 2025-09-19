#!/usr/bin/env tsx

/**
 * Validates configuration files before building
 * This ensures all required settings are present and valid
 */

import { existsSync, readFileSync } from 'fs'
import { resolve } from 'path'

import { validateSettings, validateTheme } from '../config/schemas'

const CONFIG_DIR = resolve(process.cwd(), 'config')
const SETTINGS_PATH = resolve(CONFIG_DIR, 'settings.ts')
// Try TypeScript theme first, fall back to JavaScript
const THEME_TS_PATH = resolve(CONFIG_DIR, 'theme.ts')
const THEME_JS_PATH = resolve(CONFIG_DIR, 'theme.js')
const THEME_PATH = existsSync(THEME_TS_PATH) ? THEME_TS_PATH : THEME_JS_PATH

// Console colors
const colors = {
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  reset: '\x1b[0m',
  yellow: '\x1b[33m',
}

function log(message: string, color: keyof typeof colors = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`)
}

function logError(message: string) {
  console.error(`${colors.red}❌ ${message}${colors.reset}`)
}

function logInfo(message: string) {
  log(`ℹ️  ${message}`, 'cyan')
}

function logSuccess(message: string) {
  log(`✅ ${message}`, 'green')
}

async function main() {
  log('🔍 Validating configuration files...', 'blue')
  log('='.repeat(50), 'blue')

  try {
    // Validate both config files
    const [settings, theme] = await Promise.all([
      validateSettingsFile(),
      validateThemeFile(),
    ])

    // Additional cross-validation checks
    logInfo('Running cross-validation checks...')

    // Check that theme colors are consistent
    if (theme.themeColor !== theme.primary) {
      log(
        `⚠️  Warning: themeColor (${theme.themeColor}) differs from primary color (${theme.primary})`,
        'yellow'
      )
    }

    // Check that hostnames are valid
    if (settings.TEST_HOSTNAME === settings.PROD_HOSTNAME) {
      log('⚠️  Warning: TEST_HOSTNAME and PROD_HOSTNAME are the same', 'yellow')
    }

    // Check OAuth client ID format
    if (settings.OAUTH_CLIENT_ID.length < 20) {
      log('⚠️  Warning: OAUTH_CLIENT_ID seems unusually short', 'yellow')
    }

    log('='.repeat(50), 'green')
    logSuccess('All configuration files are valid!')
    log('')
    log('Configuration summary:', 'cyan')
    log(`  Site: ${settings.SITE_NAME}`, 'cyan')
    log(`  Domain: ${settings.DOMAIN}`, 'cyan')
    log(
      `  Theme: Primary=${theme.primary}, Secondary=${theme.secondary}`,
      'cyan'
    )
    log(`  OAuth: Client ID configured`, 'cyan')
    log('')

    process.exit(0)
  } catch (error) {
    log('='.repeat(50), 'red')
    logError('Configuration validation failed!')
    log('')
    log('Please fix the errors above before building.', 'yellow')
    log('Check the example files for reference:', 'yellow')
    log('  - settings_example.js', 'yellow')
    log('  - theme_example.js', 'yellow')
    log('')
    process.exit(1)
  }
}

async function validateSettingsFile() {
  logInfo('Validating settings.ts...')

  if (!existsSync(SETTINGS_PATH)) {
    throw new Error(`Settings file not found at ${SETTINGS_PATH}`)
  }

  try {
    // Dynamic import of the settings file
    const settingsModule = await import(SETTINGS_PATH)
    const settings = settingsModule.settings

    if (!settings) {
      throw new Error('No settings export found in settings.ts')
    }

    // Validate with Zod schema
    validateSettings(settings)
    logSuccess('settings.ts is valid')
    return settings
  } catch (error) {
    if (error instanceof Error) {
      logError(`Settings validation failed: ${error.message}`)
    }
    throw error
  }
}

async function validateThemeFile() {
  const themeFileName = THEME_PATH.endsWith('.ts') ? 'theme.ts' : 'theme.js'
  logInfo(`Validating ${themeFileName}...`)

  if (!existsSync(THEME_PATH)) {
    throw new Error(`Theme file not found at ${THEME_PATH}`)
  }

  try {
    // Dynamic import of the theme file
    const themeModule = await import(THEME_PATH)
    const theme = themeModule.default

    if (!theme) {
      throw new Error(`No default export found in ${themeFileName}`)
    }

    // Validate with Zod schema
    validateTheme(theme)
    logSuccess(`${themeFileName} is valid`)
    return theme
  } catch (error) {
    if (error instanceof Error) {
      logError(`Theme validation failed: ${error.message}`)
    }
    throw error
  }
}

// Run validation
main().catch((error) => {
  console.error('Unexpected error:', error)
  process.exit(1)
})
