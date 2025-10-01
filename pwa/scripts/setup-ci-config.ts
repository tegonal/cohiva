#!/usr/bin/env tsx
/**
 * Setup CI configuration
 *
 * This script copies pre-generated tenant config for CI/CD environments.
 * Unlike setup-dev-config.ts, this NEVER generates assets - it only copies.
 *
 * Requirements:
 * - Source config must have pre-generated overlay/ directory
 * - Used in CI/CD pipelines where asset generation is not possible
 *
 * Usage:
 *   tsx setup-ci-config.ts [--config-dir path/to/config]
 */

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
  sourceConfigDir = path.isAbsolute(configDirArg)
    ? configDirArg
    : path.resolve(PWA_ROOT, configDirArg)
} else {
  sourceConfigDir = path.join(GENERATOR_ROOT, 'example-config')
}

async function main() {
  console.log('[ci-setup] Setting up CI configuration...')
  console.log('')

  // Check if source config directory exists
  if (!fs.existsSync(sourceConfigDir)) {
    console.error('[ci-setup] Error: Config directory not found at', sourceConfigDir)
    process.exit(1)
  }

  // Verify overlay exists (REQUIRED for CI)
  const overlaySource = path.join(sourceConfigDir, 'overlay')
  if (!fs.existsSync(overlaySource)) {
    console.error('[ci-setup] Error: Pre-generated overlay/ directory not found!')
    console.error('[ci-setup] Expected at:', overlaySource)
    console.error('')
    console.error('[ci-setup] CI setup requires pre-generated assets.')
    console.error('[ci-setup] Run locally: yarn generate --config-dir', path.basename(sourceConfigDir))
    console.error('[ci-setup] Then commit the overlay/ directory.')
    process.exit(1)
  }

  // Ensure config directory exists
  if (!fs.existsSync(PWA_CONFIG_DIR)) {
    fs.mkdirSync(PWA_CONFIG_DIR, { recursive: true })
  }

  // Copy config to pwa/tenant-config
  console.log('[ci-setup] Copying config to pwa/tenant-config...')

  // Get all files/directories from source config except overlay/
  const items = fs.readdirSync(sourceConfigDir)
  const filesToCopy = items.filter(
    (item) => item !== 'overlay' && !item.startsWith('.')
  )

  for (const item of filesToCopy) {
    const sourcePath = path.join(sourceConfigDir, item)
    const targetPath = path.join(PWA_CONFIG_DIR, item)

    console.log(`[ci-setup]    Copying ${item}`)
    fs.cpSync(sourcePath, targetPath, { force: true, recursive: true })
  }

  // Copy overlay files to pwa/tenant-config/overlay
  const overlayTarget = path.join(PWA_CONFIG_DIR, 'overlay')
  console.log('[ci-setup]    Copying overlay/')
  fs.cpSync(overlaySource, overlayTarget, {
    force: true,
    recursive: true,
  })

  // Copy manifest.json to public/ for dev mode
  const manifestSource = path.join(overlaySource, 'src-pwa', 'manifest.json')
  const manifestTarget = path.join(PWA_ROOT, 'public', 'manifest.json')

  if (fs.existsSync(manifestSource)) {
    console.log('[ci-setup]    Copying manifest.json to public/')
    fs.cpSync(manifestSource, manifestTarget, { force: true })
  }

  // Copy icons to public/icons/ for dev mode
  const iconsSource = path.join(overlaySource, 'public', 'icons')
  const iconsTarget = path.join(PWA_ROOT, 'public', 'icons')

  if (fs.existsSync(iconsSource)) {
    console.log('[ci-setup]    Copying icons to public/icons/')
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
      console.log(`[ci-setup]    Copying ${image} to public/`)
      fs.cpSync(imageSource, imageTarget, { force: true })
    }
  }

  console.log('')
  console.log('[ci-setup] CI configuration setup complete!')
}

main().catch((error) => {
  console.error('[ci-setup] Setup failed:', error)
  process.exit(1)
})
