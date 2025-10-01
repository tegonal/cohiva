#!/usr/bin/env tsx

/**
 * Source Config Watcher for Development
 *
 * Watches a source config directory (e.g., in pwa-tenant-config-generator)
 * and automatically regenerates and copies to local tenant-config/
 *
 * Usage:
 *   tsx watch-source-config.ts --config-dir ../pwa-tenant-config-generator/tenant-configs/my-tenant
 */

import chokidar from 'chokidar'
import { execSync } from 'node:child_process'
import * as fs from 'node:fs'
import * as path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Parse arguments
const configDirIndex = process.argv.indexOf('--config-dir')
if (configDirIndex === -1 || !process.argv[configDirIndex + 1]) {
  console.error('Error: --config-dir argument required')
  console.error('Usage: tsx watch-source-config.ts --config-dir path/to/config')
  process.exit(1)
}

const configDirArg = process.argv[configDirIndex + 1]

if (!configDirArg) {
  console.error('Error: Config directory path is missing')
  console.error('Usage: tsx watch-source-config.ts --config-dir path/to/config')
  process.exit(1)
}

const PWA_ROOT = path.resolve(__dirname, '..')
const GENERATOR_ROOT = path.resolve(PWA_ROOT, '..', 'pwa-tenant-config-generator')
const PWA_CONFIG_DIR = path.join(PWA_ROOT, 'tenant-config')

// Resolve source config directory
const sourceConfigDir = path.isAbsolute(configDirArg)
  ? configDirArg
  : path.resolve(PWA_ROOT, configDirArg)

// Validate source directory exists
if (!fs.existsSync(sourceConfigDir)) {
  console.error('Error: Config directory not found at', sourceConfigDir)
  process.exit(1)
}

// Debounce timer
let debounceTimer: NodeJS.Timeout | null = null
const DEBOUNCE_DELAY = 500
let isRebuilding = false

function handleChange(changedPath: string): void {
  const relativePath = path.relative(sourceConfigDir, changedPath)
  console.log(`[watch-source] Changed: ${relativePath}`)

  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }

  debounceTimer = setTimeout(() => {
    regenerateConfig()
  }, DEBOUNCE_DELAY)
}

async function main(): Promise<void> {
  const configName = path.basename(sourceConfigDir)
  console.log('[watch-source] Source Config Watcher Started')
  console.log(`[watch-source]    Watching: ${configName}`)
  console.log(`[watch-source]    Path: ${sourceConfigDir}`)
  console.log('[watch-source]    Press Ctrl+C to stop')
  console.log('[watch-source] ────────────────────────────────────\n')

  // Initial build
  await regenerateConfig()

  // Watch for changes (exclude overlay/ directory)
  const watchPaths = [
    path.join(sourceConfigDir, '*.js'),
    path.join(sourceConfigDir, '*.ts'),
    path.join(sourceConfigDir, '*.scss'),
    path.join(sourceConfigDir, '*.svg'),
    path.join(sourceConfigDir, '*.png'),
    path.join(sourceConfigDir, 'fonts'),
  ]

  const watcher = chokidar.watch(watchPaths, {
    awaitWriteFinish: {
      pollInterval: 100,
      stabilityThreshold: 300,
    },
    ignored: [
      '**/node_modules/**',
      '**/.git/**',
      '**/overlay/**',
      '**/.temp-*',
    ],
    ignoreInitial: true,
    persistent: true,
  })

  watcher
    .on('add', handleChange)
    .on('change', handleChange)
    .on('unlink', (changedPath) => {
      const relativePath = path.relative(sourceConfigDir, changedPath)
      console.log(`[watch-source] Removed: ${relativePath}`)
      handleChange(changedPath)
    })
    .on('error', (error) => console.error('[watch-source] Watcher error:', error))

  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n[watch-source] Stopping source config watcher...')
    watcher.close()
    process.exit(0)
  })
}

async function regenerateConfig(): Promise<void> {
  if (isRebuilding) {
    console.log('[watch-source] Rebuild already in progress...')
    return
  }

  isRebuilding = true

  try {
    console.log('[watch-source] Regenerating configuration...')
    const startTime = Date.now()

    // Generate config in pwa-tenant-config-generator
    const relativeConfigDir = path.relative(GENERATOR_ROOT, sourceConfigDir)
    try {
      execSync(`yarn generate --config-dir ${relativeConfigDir}`, {
        cwd: GENERATOR_ROOT,
        stdio: 'inherit',
      })
    } catch {
      console.error('[watch-source] Generation failed')
      return
    }

    // Copy to pwa/tenant-config
    console.log('[watch-source] Copying to tenant-config...')

    // Get all files/directories except overlay/ and dotfiles
    const items = fs.readdirSync(sourceConfigDir)
    const filesToCopy = items.filter(
      (item) => item !== 'overlay' && !item.startsWith('.')
    )

    for (const item of filesToCopy) {
      const sourcePath = path.join(sourceConfigDir, item)
      const targetPath = path.join(PWA_CONFIG_DIR, item)
      fs.cpSync(sourcePath, targetPath, { force: true, recursive: true })
    }

    // Copy overlay files
    const overlaySource = path.join(sourceConfigDir, 'overlay')
    const overlayTarget = path.join(PWA_CONFIG_DIR, 'overlay')

    if (fs.existsSync(overlaySource)) {
      fs.cpSync(overlaySource, overlayTarget, {
        force: true,
        recursive: true,
      })
    }

    const elapsed = Date.now() - startTime
    console.log(`[watch-source] Rebuild complete (${elapsed}ms)`)
    console.log('[watch-source] ────────────────────────────────────\n')
  } catch (error) {
    console.error(
      '[watch-source] Rebuild failed:',
      error instanceof Error ? error.message : String(error)
    )
  } finally {
    isRebuilding = false
  }
}

main().catch((error) => {
  console.error('[watch-source] Failed to start watcher:', error)
  process.exit(1)
})
