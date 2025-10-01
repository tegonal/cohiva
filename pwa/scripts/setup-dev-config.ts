#!/usr/bin/env tsx
/**
 * Setup development configuration
 *
 * This script:
 * 1. Installs pwa-tenant-config-generator dependencies if needed
 * 2. Copies example config to pwa/tenant-config (only if not exists)
 * 3. With --config-dir: generates and copies config from specified directory
 *
 * Usage:
 *   tsx setup-dev-config.ts [--config-dir path/to/config]
 */

import { execSync } from 'node:child_process'
import * as fs from 'node:fs'
import * as path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Parse arguments
const configDirIndex = process.argv.indexOf('--config-dir')
const configDirArg = configDirIndex !== -1 ? process.argv[configDirIndex + 1] : null

const PWA_ROOT = path.resolve(__dirname, '..')
const GENERATOR_ROOT = path.resolve(PWA_ROOT, '..', 'pwa-tenant-config-generator')
const PWA_CONFIG_DIR = path.join(PWA_ROOT, 'tenant-config')

// Determine source config directory
let sourceConfigDir: string
if (configDirArg) {
  // Custom config directory provided
  sourceConfigDir = path.isAbsolute(configDirArg)
    ? configDirArg
    : path.resolve(PWA_ROOT, configDirArg)
} else {
  // Default to example-config
  sourceConfigDir = path.join(GENERATOR_ROOT, 'example-config')
}

async function main() {
  const overlayTarget = path.join(PWA_CONFIG_DIR, 'overlay')

  // In regular dev mode with no custom config, only setup if config doesn't exist
  if (!configDirArg && fs.existsSync(overlayTarget)) {
    return // Silent skip in regular mode
  }

  // Check if pwa-tenant-config-generator directory exists
  if (!fs.existsSync(GENERATOR_ROOT)) {
    console.error('[setup] Error: pwa-tenant-config-generator directory not found at', GENERATOR_ROOT)
    console.error('[setup] Expected structure: cohiva/pwa and cohiva/pwa-tenant-config-generator')
    process.exit(1)
  }

  // Check if source config directory exists
  if (!fs.existsSync(sourceConfigDir)) {
    console.error('[setup] Error: Config directory not found at', sourceConfigDir)
    process.exit(1)
  }

  // Ensure config directory exists
  if (!fs.existsSync(PWA_CONFIG_DIR)) {
    fs.mkdirSync(PWA_CONFIG_DIR, { recursive: true })
  }

  // Install pwa-tenant-config-generator dependencies if needed
  const generatorNodeModules = path.join(GENERATOR_ROOT, 'node_modules')
  if (!fs.existsSync(generatorNodeModules)) {
    console.log('[setup] Installing pwa-tenant-config-generator dependencies...')
    execSync('yarn install', {
      cwd: GENERATOR_ROOT,
      stdio: 'inherit',
    })
    console.log('')
  }

  // Generate and copy config
  if (configDirArg || !fs.existsSync(overlayTarget)) {
    const configName = path.basename(sourceConfigDir)
    console.log(
      configDirArg
        ? `[setup] Setting up configuration from ${configName}...`
        : '[setup] Setting up development configuration...'
    )
    console.log('')

    // Generate config in pwa-tenant-config-generator
    const relativeConfigDir = path.relative(GENERATOR_ROOT, sourceConfigDir)
    console.log(`[setup] Generating config from ${relativeConfigDir}...`)
    try {
      execSync(`yarn generate --config-dir ${relativeConfigDir}`, {
        cwd: GENERATOR_ROOT,
        stdio: 'inherit',
      })
    } catch {
      console.error('[setup] Failed to generate config')
      process.exit(1)
    }
    console.log('')

    // Copy config to pwa/tenant-config
    console.log('[setup] Copying config to pwa/tenant-config...')

    // Get all files/directories from source config except overlay/
    const items = fs.readdirSync(sourceConfigDir)
    const filesToCopy = items.filter(
      (item) => item !== 'overlay' && !item.startsWith('.')
    )

    for (const item of filesToCopy) {
      const sourcePath = path.join(sourceConfigDir, item)
      const targetPath = path.join(PWA_CONFIG_DIR, item)

      console.log(`[setup]    Copying ${item}`)
      fs.cpSync(sourcePath, targetPath, { force: true, recursive: true })
    }

    // Copy overlay files to pwa/tenant-config/overlay
    const overlaySource = path.join(sourceConfigDir, 'overlay')

    if (fs.existsSync(overlaySource)) {
      console.log('[setup]    Copying overlay/')
      fs.cpSync(overlaySource, overlayTarget, {
        force: true,
        recursive: true,
      })
    }

    // Copy manifest.json to public/ for dev mode
    const manifestSource = path.join(overlaySource, 'src-pwa', 'manifest.json')
    const manifestTarget = path.join(PWA_ROOT, 'public', 'manifest.json')

    if (fs.existsSync(manifestSource)) {
      console.log('[setup]    Copying manifest.json to public/')
      fs.cpSync(manifestSource, manifestTarget, { force: true })
    }

    // Copy icons to public/icons/ for dev mode
    const iconsSource = path.join(overlaySource, 'public', 'icons')
    const iconsTarget = path.join(PWA_ROOT, 'public', 'icons')

    if (fs.existsSync(iconsSource)) {
      console.log('[setup]    Copying icons to public/icons/')
      fs.cpSync(iconsSource, iconsTarget, { force: true, recursive: true })
    }

    // Copy social media images to public root for dev mode
    const publicSource = path.join(overlaySource, 'public')
    const publicTarget = path.join(PWA_ROOT, 'public')
    const socialImages = ['og-image.png', 'twitter-card.png']

    for (const image of socialImages) {
      const imageSource = path.join(publicSource, image)
      const imageTarget = path.join(publicTarget, image)

      if (fs.existsSync(imageSource)) {
        console.log(`[setup]    Copying ${image} to public/`)
        fs.cpSync(imageSource, imageTarget, { force: true })
      }
    }

    console.log('')
    console.log('[setup] Configuration setup complete!')
  }
}

main().catch((error) => {
  console.error('[setup] Setup failed:', error)
  process.exit(1)
})
