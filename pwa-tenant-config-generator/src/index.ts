#!/usr/bin/env tsx

/**
 * PWA Tools - Tenant Configuration Generator
 *
 * Generates tenant-specific PWA configuration and assets
 * Usage: tsx src/index.ts --config-dir <path-to-tenant-config>
 */

import { parseArgs } from 'node:util'

import { generateTenantConfig } from './generator.js'

const { values } = parseArgs({
  options: {
    'config-dir': {
      short: 'c',
      type: 'string',
    },
    help: {
      short: 'h',
      type: 'boolean',
    },
  },
})

if (values.help) {
  console.log(`
PWA Tools - Tenant Configuration Generator

Usage:
  tsx src/index.ts --config-dir <path>
  yarn generate --config-dir <path>

Options:
  -c, --config-dir <path>    Path to tenant configuration directory (required)
  -h, --help                 Show this help message

Example:
  yarn generate --config-dir ../pwa/config
`)
  process.exit(0)
}

if (!values['config-dir']) {
  console.error('[ERROR] Error: --config-dir is required')
  console.error('Run with --help for usage information')
  process.exit(1)
}

// Run generator
generateTenantConfig(values['config-dir'])
  .then(() => {
    console.log('[SUCCESS] Tenant configuration generated successfully!')
    process.exit(0)
  })
  .catch((error: Error) => {
    console.error('[ERROR] Generation failed:', error.message)
    process.exit(1)
  })
