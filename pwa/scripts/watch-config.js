#!/usr/bin/env node

/**
 * Config Watcher for Development
 * 
 * Watches the config directory for changes and automatically runs
 * the make-tenant-config script to regenerate assets and styles.
 */

import fs from 'fs-extra'
import path from 'path'
import { exec } from 'child_process'
import { promisify } from 'util'
import { fileURLToPath } from 'url'
import chokidar from 'chokidar'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const rootDir = path.resolve(__dirname, '..')
const execAsync = promisify(exec)

// Debounce timer to avoid multiple rapid rebuilds
let debounceTimer = null
const DEBOUNCE_DELAY = 500 // ms

// Track if a build is currently running
let isBuilding = false

// Files and directories to watch
const watchPaths = [
  path.join(rootDir, 'config', '*.js'),
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

async function runMakeTenantConfig() {
  if (isBuilding) {
    console.log('⏳ Build already in progress, queueing next build...')
    return
  }

  isBuilding = true
  
  try {
    console.log('\n🔄 Config change detected, rebuilding...')
    const startTime = Date.now()
    
    const { stdout, stderr } = await execAsync('node scripts/make-tenant-config.js', { 
      cwd: rootDir 
    })
    
    if (stderr && !stderr.includes('Warning')) {
      console.error('⚠️  Build warnings:', stderr)
    }
    
    const elapsed = Date.now() - startTime
    console.log(`✅ Rebuild complete (${elapsed}ms)`)
    
    // Show key outputs
    const lines = stdout.split('\n')
    const importantLines = lines.filter(line => 
      line.includes('✅') || 
      line.includes('⚠️') || 
      line.includes('Site:') || 
      line.includes('Theme:')
    )
    
    if (importantLines.length > 0) {
      console.log('\n' + importantLines.slice(-3).join('\n'))
    }
    
  } catch (error) {
    console.error('❌ Build failed:', error.message)
  } finally {
    isBuilding = false
  }
}

function handleChange(path) {
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

async function startWatcher() {
  console.log('👀 Config Watcher Started')
  console.log('   Watching for changes in:')
  console.log('   - config/*.js (settings, theme)')
  console.log('   - config/*.scss (webfonts, override)')
  console.log('   - config/*.svg, *.png (logo, icon)')
  console.log('   - config/fonts/* (font files)')
  console.log('\n   Press Ctrl+C to stop')
  console.log('   ────────────────────────────────────')
  
  // Run initial build
  await runMakeTenantConfig()
  
  // Create watcher
  const watcher = chokidar.watch(watchPaths, {
    ignored: ignorePaths,
    persistent: true,
    ignoreInitial: true,
    awaitWriteFinish: {
      stabilityThreshold: 300,
      pollInterval: 100
    }
  })
  
  // Watch for changes
  watcher
    .on('add', path => {
      console.log(`➕ Added: ${path.replace(rootDir + '/', '')}`)
      handleChange(path)
    })
    .on('change', handleChange)
    .on('unlink', path => {
      console.log(`➖ Removed: ${path.replace(rootDir + '/', '')}`)
      handleChange(path)
    })
    .on('error', error => console.error('❌ Watcher error:', error))
  
  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n\n👋 Stopping config watcher...')
    watcher.close()
    process.exit(0)
  })
}

// Check if chokidar is installed
async function checkDependencies() {
  try {
    await import('chokidar')
    return true
  } catch (error) {
    console.error('❌ Missing dependency: chokidar')
    console.log('\n   Please install it with:')
    console.log('   yarn add -D chokidar')
    console.log('\n   or')
    console.log('   npm install --save-dev chokidar\n')
    return false
  }
}

// Main
async function main() {
  if (!await checkDependencies()) {
    process.exit(1)
  }
  
  startWatcher().catch(error => {
    console.error('❌ Failed to start watcher:', error)
    process.exit(1)
  })
}

main()