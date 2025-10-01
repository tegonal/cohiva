#!/usr/bin/env tsx

/**
 * Development server with custom tenant config watcher
 *
 * Usage:
 *   tsx scripts/dev-with-tenant.ts ../pwa-tenant-config-generator/tenant-configs/my-tenant
 */

import { spawn } from 'node:child_process'
import { execSync } from 'node:child_process'
import * as path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const configDir = process.argv[2]

if (!configDir) {
  console.error('Error: Config directory argument required')
  console.error('Usage: yarn dev:tenant path/to/tenant-config')
  process.exit(1)
}

const rootDir = path.resolve(__dirname, '..')

console.log('[dev-tenant] Setting up tenant configuration...')
try {
  execSync(`tsx scripts/setup-dev-config.ts --config-dir "${configDir}"`, {
    cwd: rootDir,
    stdio: 'inherit',
  })
} catch {
  console.error('[dev-tenant] Failed to setup configuration')
  process.exit(1)
}

console.log('[dev-tenant] Validating configuration...')
try {
  execSync('yarn validate:config', {
    cwd: rootDir,
    stdio: 'inherit',
  })
} catch {
  console.error('[dev-tenant] Configuration validation failed')
  process.exit(1)
}

console.log('[dev-tenant] Starting watcher and dev server...\n')

// Run concurrently
const concurrently = spawn(
  'npx',
  [
    'concurrently',
    '-n',
    'watch,dev',
    '-c',
    'cyan,green',
    `tsx scripts/watch-source-config.ts --config-dir ${configDir}`,
    'quasar dev',
  ],
  {
    cwd: rootDir,
    shell: true,
    stdio: 'inherit',
  }
)

concurrently.on('exit', (code) => {
  process.exit(code || 0)
})

// Handle Ctrl+C
process.on('SIGINT', () => {
  concurrently.kill('SIGINT')
  process.exit(0)
})
