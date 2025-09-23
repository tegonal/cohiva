#!/usr/bin/env tsx

/**
 * Config Watcher for Development
 *
 * Watches the config directory for changes and automatically runs
 * the make-tenant-config script to regenerate assets and styles.
 */

import { exec } from 'child_process'
import chokidar from 'chokidar'
import path from 'path'
import { fileURLToPath } from 'url'
import { promisify } from 'util'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const rootDir = path.resolve(__dirname, '..')
const execAsync = promisify(exec)

// Debounce timer to avoid multiple rapid rebuilds
let debounceTimer: NodeJS.Timeout | null = null
const DEBOUNCE_DELAY = 500 // ms

// Track if a build is currently running
let isBuilding = false

// Files and directories to watch
const watchPaths = [
  path.join(rootDir, 'config', '*.js'),
  path.join(rootDir, 'config', '*.ts'), // Include TypeScript config files
  path.join(rootDir, 'config', '*.scss'),
  path.join(rootDir, 'config', '*.svg'),
  path.join(rootDir, 'config', '*.png'),
  path.join(rootDir, 'config', 'fonts'),
]

// Files to ignore (avoid watching generated files)
const ignorePaths = [
  '**/node_modules/**',
  '**/.git/**',
  '**/dist/**',
  '**/.quasar/**',
  '**/src/css/app.scss',
  '**/src/css/override.scss',
  '**/src/css/webfonts.scss',
  '**/src/css/fonts/**',
  '**/src/assets/logo.svg',
  '**/src/assets/icon.svg',
  '**/.temp-*',
]

// Check if chokidar is installed
async function checkDependencies(): Promise<boolean> {
  try {
    await import('chokidar')
    return true
  } catch {
    console.error('❌ Missing dependency: chokidar')
    console.log('\n   Please install it with:')
    console.log('   yarn add -D chokidar')
    console.log('\n   or')
    console.log('   npm install --save-dev chokidar\n')
    return false
  }
}

function handleChange(path: string): void {
  const relativePath = path.replace(rootDir + '/', '')
  console.log(`📝 Changed: ${relativePath}`)

  // Clear existing timer
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }

  // Set new timer
  debounceTimer = setTimeout(() => {
    runMakeTenantConfig()
  }, DEBOUNCE_DELAY)
}

// Main
async function main(): Promise<void> {
  if (!(await checkDependencies())) {
    process.exit(1)
  }

  startWatcher().catch((error) => {
    console.error('❌ Failed to start watcher:', error)
    process.exit(1)
  })
}

async function runMakeTenantConfig(): Promise<void> {
  if (isBuilding) {
    console.log('⏳ Build already in progress, queueing next build...')
    return
  }

  isBuilding = true

  try {
    console.log('\n🔄 Config change detected, validating and rebuilding...')
    const startTime = Date.now()

    // First validate the configuration
    console.log('🔍 Validating configuration...')
    try {
      await execAsync('yarn validate:config', {
        cwd: rootDir,
      })
      console.log('✅ Configuration valid')
    } catch (validationError) {
      console.error('❌ Configuration validation failed!')
      if (validationError instanceof Error) {
        console.error(validationError.message)
      }
      console.log('⚠️  Fix the configuration errors before continuing')
      return
    }

    // Then run make-tenant-config
    const { stderr, stdout } = await execAsync(
      'node scripts/make-tenant-config.js',
      {
        cwd: rootDir,
      }
    )

    if (stderr && !stderr.includes('Warning')) {
      console.error('⚠️  Build warnings:', stderr)
    }

    const elapsed = Date.now() - startTime
    console.log(`✅ Rebuild complete (${elapsed}ms)`)

    // Show key outputs
    const lines = stdout.split('\n')
    const importantLines = lines.filter(
      (line) =>
        line.includes('✅') ||
        line.includes('⚠️') ||
        line.includes('Site:') ||
        line.includes('Theme:')
    )

    if (importantLines.length > 0) {
      console.log('\n' + importantLines.slice(-3).join('\n'))
    }
  } catch (error) {
    console.error(
      '❌ Build failed:',
      error instanceof Error ? error.message : String(error)
    )
  } finally {
    isBuilding = false
  }
}

async function startWatcher(): Promise<void> {
  console.log('👀 Config Watcher Started')
  console.log('   Watching for changes in:')
  console.log('   - config/*.ts, *.js (settings, theme, schemas)')
  console.log('   - config/*.scss (webfonts, override)')
  console.log('   - config/*.svg, *.png (logo, icon)')
  console.log('   - config/fonts/* (font files)')
  console.log('\n   Press Ctrl+C to stop')
  console.log('   ────────────────────────────────────')

  // Run initial build
  await runMakeTenantConfig()

  // Create watcher
  const watcher = chokidar.watch(watchPaths, {
    awaitWriteFinish: {
      pollInterval: 100,
      stabilityThreshold: 300,
    },
    ignored: ignorePaths,
    ignoreInitial: true,
    persistent: true,
  })

  // Watch for changes
  watcher
    .on('add', (path) => {
      console.log(`➕ Added: ${path.replace(rootDir + '/', '')}`)
      handleChange(path)
    })
    .on('change', handleChange)
    .on('unlink', (path) => {
      console.log(`➖ Removed: ${path.replace(rootDir + '/', '')}`)
      handleChange(path)
    })
    .on('error', (error) => console.error('❌ Watcher error:', error))

  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n\n👋 Stopping config watcher...')
    watcher.close()
    process.exit(0)
  })
}

main()
