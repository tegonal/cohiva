#!/usr/bin/env tsx

/**
 * Make Tenant Config Script
 *
 * This script generates tenant-specific configuration for the PWA by:
 * 1. Setting up logo and icon files from config/
 * 2. Converting SVG to PNG if needed (with resolution check)
 * 3. Generating PWA assets using Icon Genie
 * 4. Creating manifest.json with tenant settings
 * 5. Setting up web fonts from config/fonts/
 * 6. Generating app.scss with theme colors
 * 7. Copying override.scss for tenant customizations
 *
 * Usage:
 *   node scripts/make-tenant-config.js
 *
 * The script uses files from the config/ directory to generate
 * all tenant-specific assets and styles.
 */

import { exec } from 'child_process'
import fs from 'fs-extra'
import path from 'path'
import sharp from 'sharp'
import { fileURLToPath } from 'url'
import { promisify } from 'util'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const rootDir = path.resolve(__dirname, '..')

const execAsync = promisify(exec)

// Minimum resolution for PWA assets (Icon Genie requirement)
const MIN_ICON_SIZE = 1024

interface VerificationResult {
  foundFiles: string[]
  generatedFiles: string[]
  missingFiles: string[]
  success: boolean
  unreferencedFiles: string[]
}

async function checkImageResolution(imagePath: string): Promise<boolean> {
  try {
    const metadata = await sharp(imagePath).metadata()
    console.log(`   Image dimensions: ${metadata.width}x${metadata.height}`)

    if (metadata.width < MIN_ICON_SIZE || metadata.height < MIN_ICON_SIZE) {
      console.warn(
        `   ⚠️  Image resolution too low! Minimum required: ${MIN_ICON_SIZE}x${MIN_ICON_SIZE}`
      )
      return false
    }

    return true
  } catch (error) {
    console.error(
      '   Failed to check image resolution:',
      error instanceof Error ? error.message : String(error)
    )
    return false
  }
}

async function convertSvgToPng(
  svgPath: string,
  outputPath: string,
  size = MIN_ICON_SIZE
): Promise<string> {
  try {
    console.log(`   Converting SVG to PNG (${size}x${size})...`)

    // Read SVG file
    const svgBuffer = await fs.readFile(svgPath)

    // Convert SVG to PNG with specified size
    await sharp(svgBuffer)
      .resize(size, size, {
        background: { alpha: 0, b: 0, g: 0, r: 0 }, // Transparent background
        fit: 'contain',
      })
      .png()
      .toFile(outputPath)

    console.log(`   ✅ PNG created successfully`)
    return outputPath
  } catch (error) {
    console.error(
      '   ❌ SVG to PNG conversion failed:',
      error instanceof Error ? error.message : String(error)
    )
    throw error
  }
}

async function generateSocialCards(
  logoPath: string,
  backgroundColor: string
): Promise<boolean> {
  console.log('🎴 Generating social media cards...')

  try {
    // Parse background color (remove # if present)
    const bgColor = backgroundColor.replace('#', '')
    const r = parseInt(bgColor.substr(0, 2), 16)
    const g = parseInt(bgColor.substr(2, 2), 16)
    const b = parseInt(bgColor.substr(4, 2), 16)

    // Read logo
    const logoBuffer = await fs.readFile(logoPath)

    // Generate Open Graph image (1200x630 - Facebook, LinkedIn, etc.)
    console.log('   Generating Open Graph image (1200x630)...')
    const ogBackground = await sharp({
      create: {
        background: { b, g, r },
        channels: 3,
        height: 630,
        width: 1200,
      },
    })
      .png()
      .toBuffer()

    // Resize logo to fit nicely (40% of the smaller dimension)
    const ogLogoSize = Math.floor(Math.min(1200, 630) * 0.4)
    const ogLogo = await sharp(logoBuffer)
      .resize(ogLogoSize, ogLogoSize, {
        background: { alpha: 0, b, g, r },
        fit: 'contain',
      })
      .png()
      .toBuffer()

    // Composite logo on background
    await sharp(ogBackground)
      .composite([
        {
          gravity: 'center',
          input: ogLogo,
        },
      ])
      .png()
      .toFile(path.join(rootDir, 'public', 'og-image.png'))

    console.log('   ✅ Open Graph image created')

    // Generate Twitter card image (1200x600 - 2:1 ratio)
    console.log('   Generating Twitter card image (1200x600)...')
    const twitterBackground = await sharp({
      create: {
        background: { b, g, r },
        channels: 3,
        height: 600,
        width: 1200,
      },
    })
      .png()
      .toBuffer()

    // Resize logo for Twitter card
    const twitterLogoSize = Math.floor(Math.min(1200, 600) * 0.4)
    const twitterLogo = await sharp(logoBuffer)
      .resize(twitterLogoSize, twitterLogoSize, {
        background: { alpha: 0, b, g, r },
        fit: 'contain',
      })
      .png()
      .toBuffer()

    // Composite logo on background
    await sharp(twitterBackground)
      .composite([
        {
          gravity: 'center',
          input: twitterLogo,
        },
      ])
      .png()
      .toFile(path.join(rootDir, 'public', 'twitter-card.png'))

    console.log('   ✅ Twitter card image created')

    return true
  } catch (error) {
    console.error(
      '   ❌ Failed to generate social cards:',
      error instanceof Error ? error.message : String(error)
    )
    return false
  }
}

async function makeTenantConfig(): Promise<void> {
  console.log('🚀 Generating tenant configuration...')

  try {
    // 1. Setup logo
    console.log('🎨 Setting up logo...')
    const logoSource = path.join(rootDir, 'config', 'logo.svg')
    const logoTarget = path.join(rootDir, 'src', 'assets', 'logo.svg')

    // Check if logo.svg exists
    const hasLogo = await fs.pathExists(logoSource)

    if (!hasLogo) {
      throw new Error('config/logo.svg is required')
    }

    // Copy logo.svg to assets
    await fs.remove(logoTarget)
    await fs.copy(logoSource, logoTarget)

    // Setup dark mode variant for logo
    console.log('🌙 Setting up dark mode logo...')
    const logoDarkSource = path.join(rootDir, 'config', 'logo-dark.svg')
    const logoDarkTarget = path.join(rootDir, 'src', 'assets', 'logo-dark.svg')

    // Check if dark mode logo exists
    const hasLogoDark = await fs.pathExists(logoDarkSource)

    if (!hasLogoDark) {
      throw new Error('config/logo-dark.svg is required for dark mode support')
    }

    // Copy logo-dark.svg to assets
    await fs.remove(logoDarkTarget)
    await fs.copy(logoDarkSource, logoDarkTarget)
    console.log('   ✅ Copied logo-dark.svg')

    // 2. Load theme and settings
    // Try TypeScript theme first, fall back to JavaScript
    let themePath = path.join(rootDir, 'config', 'theme.ts')
    if (!(await fs.pathExists(themePath))) {
      themePath = path.join(rootDir, 'config', 'theme.js')
    }
    const theme = await import(themePath)
    const { settings } = await import(
      path.join(rootDir, 'config', 'settings.js')
    )

    // Validate theme configuration
    const { validateTheme } = await import(
      path.join(rootDir, 'config', 'schemas.js')
    )
    try {
      validateTheme(theme.default)
      console.log('✅ Theme configuration validated')
    } catch (error) {
      console.error('❌ Theme validation failed:', error)
      process.exit(1)
    }

    // 3. Prepare icon and logo for Icon Genie
    console.log('🖼️  Preparing assets for PWA generation...')

    // Check if we have separate icon and logo files
    const iconSvgPath = path.join(rootDir, 'config', 'app-icon.svg')
    const iconPngPath = path.join(rootDir, 'config', 'app-icon.png')
    const logoSvgPath = path.join(rootDir, 'config', 'logo.svg')
    const logoPngPath = path.join(rootDir, 'config', 'logo.png')
    const tempIconPngPath = path.join(rootDir, 'config', '.temp-icon.png')
    const tempLogoPngPath = path.join(rootDir, 'config', '.temp-logo.png')

    let iconSourcePath

    // Prepare icon source (for app icons)
    console.log('   Preparing icon for app icons...')
    if (await fs.pathExists(iconPngPath)) {
      console.log('   Found app-icon.png, checking resolution...')
      if (await checkImageResolution(iconPngPath)) {
        iconSourcePath = iconPngPath
      } else {
        console.log('   Icon PNG resolution too low, converting from SVG...')
        if (await fs.pathExists(iconSvgPath)) {
          iconSourcePath = await convertSvgToPng(
            iconSvgPath,
            tempIconPngPath,
            MIN_ICON_SIZE
          )
        } else {
          throw new Error(
            'Icon PNG resolution too low and no app-icon.svg available'
          )
        }
      }
    } else if (await fs.pathExists(iconSvgPath)) {
      console.log('   Found app-icon.svg, converting to PNG...')
      iconSourcePath = await convertSvgToPng(
        iconSvgPath,
        tempIconPngPath,
        MIN_ICON_SIZE
      )
    } else {
      // Fallback to logo if no icon exists
      console.log('   No app-icon.svg/png found, using logo for icons...')
      if (
        (await fs.pathExists(logoPngPath)) &&
        (await checkImageResolution(logoPngPath))
      ) {
        iconSourcePath = logoPngPath
      } else if (await fs.pathExists(logoSvgPath)) {
        iconSourcePath = await convertSvgToPng(
          logoSvgPath,
          tempIconPngPath,
          MIN_ICON_SIZE
        )
      } else {
        throw new Error('No icon or logo files found in config directory')
      }
    }

    // Verify logo exists (needed for social media cards)
    if (!(await fs.pathExists(logoSvgPath))) {
      throw new Error('No logo.svg found in config directory')
    }

    // 4. Generate social media cards
    await generateSocialCards(logoSvgPath, theme.default.backgroundColor)

    // 5. Generate PWA assets with Icon Genie
    console.log('🎨 Generating PWA assets with Icon Genie...')
    const themeColor = theme.default.primary.replace('#', '')
    const backgroundColor = theme.default.backgroundColor.replace('#', '')

    try {
      // Icon Genie limitation: it uses the same image for both app icons and splash screen overlays
      // We'll use the icon for both - it's designed to work well at small sizes
      // The icon will be used for:
      // - App icons (at appropriate sizes)
      // - Splash screens (centered at 40% size on background color)
      // No padding: icon should use full available space as designed
      // Always skip trim to preserve icon aspect ratio and prevent unwanted cropping
      const iconGenieCmd =
        `npx icongenie generate -m pwa -i "${iconSourcePath}" --theme-color ${themeColor} --png-color ${backgroundColor} --splashscreen-color ${backgroundColor} --splashscreen-icon-ratio 40 --quality 10 --skip-trim`.trim()
      console.log(`   Running: ${iconGenieCmd}`)

      const { stderr, stdout } = await execAsync(iconGenieCmd, { cwd: rootDir })

      if (stdout) console.log(stdout)
      if (stderr && !stderr.includes('Warning')) console.error(stderr)

      console.log('✅ PWA assets generated successfully')

      // Note: Icon Genie generates files in public/icons/
      // During build, Vite copies public files to dist root
      // Files are referenced as "icons/icon-*.png" (no leading slash)

      // Optimize generated icons
      console.log('🖼️  Optimizing generated PWA icons...')
      const optimizeCmd = 'tsx scripts/optimize-images.ts public/icons'
      console.log(`   Running: ${optimizeCmd}`)

      try {
        const { stderr: optStderr, stdout: optStdout } = await execAsync(
          optimizeCmd,
          { cwd: rootDir }
        )

        if (optStdout) console.log(optStdout)
        if (optStderr && !optStderr.includes('Warning'))
          console.error(optStderr)

        console.log('✅ Icons optimized successfully')
      } catch (optError) {
        console.error(
          '⚠️  Failed to optimize icons:',
          optError instanceof Error ? optError.message : String(optError)
        )
        // Don't throw - optimization is nice to have but not critical
      }

      // Clean up temp files if created
      if (await fs.pathExists(tempIconPngPath)) {
        await fs.remove(tempIconPngPath)
      }
      if (await fs.pathExists(tempLogoPngPath)) {
        await fs.remove(tempLogoPngPath)
      }
    } catch (error) {
      console.error(
        '❌ Icon generation failed:',
        error instanceof Error ? error.message : String(error)
      )
      console.log(
        '   Make sure Icon Genie is installed: yarn add -D @quasar/icongenie'
      )

      // Clean up temp files even on error
      if (await fs.pathExists(tempIconPngPath)) {
        await fs.remove(tempIconPngPath)
      }
      if (await fs.pathExists(tempLogoPngPath)) {
        await fs.remove(tempLogoPngPath)
      }

      throw error
    }

    // 6. Generate manifest.json
    console.log('📋 Generating manifest.json...')
    const manifest = {
      background_color: theme.default.backgroundColor,
      description:
        settings.siteDescription || `${settings.siteName} Progressive Web App`,
      display: 'standalone',
      icons: [
        {
          sizes: '128x128',
          src: 'icons/icon-128x128.png',
          type: 'image/png',
        },
        {
          sizes: '192x192',
          src: 'icons/icon-192x192.png',
          type: 'image/png',
        },
        {
          sizes: '256x256',
          src: 'icons/icon-256x256.png',
          type: 'image/png',
        },
        {
          sizes: '384x384',
          src: 'icons/icon-384x384.png',
          type: 'image/png',
        },
        {
          sizes: '512x512',
          src: 'icons/icon-512x512.png',
          type: 'image/png',
        },
      ],
      id: `/${settings.appBasename}/`,
      name: settings.siteName,
      orientation: 'portrait',
      short_name: settings.siteNickname,
      start_url: '/',
      theme_color: theme.default.primary,
    }

    const manifestPath = path.join(rootDir, 'src-pwa', 'manifest.json')
    await fs.ensureDir(path.dirname(manifestPath))
    await fs.writeJson(manifestPath, manifest, { spaces: 2 })

    // 7. Setup web fonts
    console.log('🔤 Setting up web fonts...')
    const fontsSource = path.join(rootDir, 'config', 'fonts')
    const fontsTarget = path.join(rootDir, 'src', 'css', 'fonts')
    const webfontsSource = path.join(rootDir, 'config', 'webfonts.scss')
    const webfontsTarget = path.join(rootDir, 'src', 'css', 'webfonts.scss')

    // Copy fonts directory if it exists and has files
    if (await fs.pathExists(fontsSource)) {
      const fontFiles = await fs.readdir(fontsSource)
      const actualFonts = fontFiles.filter((f) => !f.startsWith('.')) // Exclude .gitkeep, etc

      if (actualFonts.length > 0) {
        console.log(
          `   Found ${actualFonts.length} font file(s), copying to src/css/fonts...`
        )
        await fs.ensureDir(fontsTarget)
        await fs.copy(fontsSource, fontsTarget)
      } else {
        console.log('   No font files found in config/fonts')
      }
    }

    // Copy webfonts.scss if it exists
    if (await fs.pathExists(webfontsSource)) {
      console.log('   Found webfonts.scss, copying to src/css...')
      await fs.copy(webfontsSource, webfontsTarget)
    } else {
      console.log('   No webfonts.scss found, creating default...')
      // Create a minimal webfonts.scss that sets the default font variable
      const defaultWebfonts = `// Default web fonts configuration
// Place custom font definitions in config/webfonts.scss

// Default Quasar font family
$typography-font-family: 'Roboto', 'Helvetica Neue', Helvetica, Arial, sans-serif !default;
`
      await fs.writeFile(webfontsTarget, defaultWebfonts)
    }

    // 8. Generate quasar.variables.scss from theme.js
    console.log('🎨 Generating quasar.variables.scss from theme colors...')

    // Skip these variables (they're for app config, not SCSS)
    const skipVars = [
      'backgroundColor',
      'themeColor',
      'splashBackgroundColor',
      'splashIconColor',
    ]

    // Simply output all theme variables as SCSS
    let scssVariables = ''
    for (const [key, value] of Object.entries(theme.default)) {
      if (value && !skipVars.includes(key)) {
        scssVariables += `$${key}: ${value};\n`
      }
    }

    const quasarVariablesContent = `// Generated from config/theme.ts
// Do not edit directly - modify config/theme.ts instead

// Quasar SCSS (& Sass) Variables
// --------------------------------------------------
// To customize the look and feel of this app, you can override
// the Sass/SCSS variables found in Quasar's source Sass/SCSS files.

// Check documentation for full list of Quasar variables

// Your own variables (that are declared here) and Quasar's own
// ones will be available out of the box in your .vue/.scss/.sass files

${scssVariables}
`

    const quasarVariablesPath = path.join(
      rootDir,
      'src',
      'css',
      'quasar.variables.scss'
    )
    await fs.writeFile(quasarVariablesPath, quasarVariablesContent)

    // 9. Generate app.scss with custom styles
    console.log('🎨 Generating app.scss with custom styles...')
    const appScssContent = `// Generated from config/theme.js
// Do not edit directly - modify config/theme.js instead

// Import web fonts first (this sets font variables)
@import './webfonts.scss';

// Custom app styles
.app-logo {
  height: 40px;
  width: auto;
}

// Additional custom styles can be added below
`

    const appScssPath = path.join(rootDir, 'src', 'css', 'app.scss')
    await fs.writeFile(appScssPath, appScssContent)

    // 10. Copy override.scss if it exists
    console.log('🎨 Setting up style overrides...')
    const overrideSource = path.join(rootDir, 'config', 'override.scss')
    const overrideTarget = path.join(rootDir, 'src', 'css', 'override.scss')

    if (await fs.pathExists(overrideSource)) {
      console.log('   Found override.scss, copying to src/css...')
      await fs.copy(overrideSource, overrideTarget)
    } else {
      console.log('   No override.scss found, creating empty file...')
      // Create an empty override file so imports don't break
      await fs.writeFile(overrideTarget, '// No tenant-specific overrides\n')
    }

    // 10. Verify index.html matches Icon Genie output
    await verifyIconReferences()

    console.log('✅ Tenant configuration complete!')
    console.log(`   Site: ${settings.siteName}`)
    console.log(`   Theme: ${theme.default.primary}`)
    console.log(`   Background: ${theme.default.backgroundColor}`)
  } catch (error) {
    console.error('❌ Tenant configuration failed:', error)
    process.exit(1)
  }
}

async function verifyIconReferences(): Promise<VerificationResult> {
  console.log('🔍 Verifying icon and splash screen references in index.html...')

  const indexPath = path.join(rootDir, 'index.html')

  try {
    // Read index.html
    const indexContent = await fs.readFile(indexPath, 'utf-8')

    // Extract all icon and splash screen references
    const iconPattern =
      /<link[^>]+rel=["'](?:icon|apple-touch-icon|mask-icon)["'][^>]*>/gi
    const splashPattern =
      /<link[^>]+rel=["']apple-touch-startup-image["'][^>]*>/gi
    const metaPattern =
      /<meta[^>]+name=["'](?:msapplication-TileImage|msapplication-config)["'][^>]*>/gi

    const iconMatches = indexContent.match(iconPattern) || []
    const splashMatches = indexContent.match(splashPattern) || []
    const metaMatches = indexContent.match(metaPattern) || []

    const allReferences = [...iconMatches, ...splashMatches, ...metaMatches]

    const missingFiles: string[] = []
    const foundFiles: string[] = []

    // Check each reference
    for (const tag of allReferences) {
      // Extract href or content attribute value
      const hrefMatch = tag.match(/(?:href|content)=["']([^"']+)["']/)
      if (hrefMatch && hrefMatch[1]) {
        const filePath = hrefMatch[1]

        // Skip data URLs and external URLs
        if (filePath.startsWith('data:') || filePath.startsWith('http')) {
          continue
        }

        // Build the full path (remove leading slash if present)
        const cleanPath = filePath.replace(/^\//, '')
        const fullPath = path.join(rootDir, 'public', cleanPath)

        // Check if file exists
        if (await fs.pathExists(fullPath)) {
          foundFiles.push(cleanPath)
        } else {
          missingFiles.push(cleanPath)
        }
      }
    }

    // Expected Icon Genie PWA files (default set)
    const expectedIconGenieFiles = [
      'favicon.ico', // In public root, not icons folder
      'icons/favicon-16x16.png',
      'icons/favicon-32x32.png',
      'icons/favicon-96x96.png',
      'icons/favicon-128x128.png',
      'icons/icon-128x128.png',
      'icons/icon-192x192.png',
      'icons/icon-256x256.png',
      'icons/icon-384x384.png',
      'icons/icon-512x512.png',
      'icons/ms-icon-144x144.png',
      'icons/apple-icon-120x120.png',
      'icons/apple-icon-152x152.png',
      'icons/apple-icon-167x167.png',
      'icons/apple-icon-180x180.png',
      'icons/safari-pinned-tab.svg',
      'icons/apple-launch-640x1136.png',
      'icons/apple-launch-750x1334.png',
      'icons/apple-launch-828x1792.png',
      'icons/apple-launch-1125x2436.png',
      'icons/apple-launch-1242x2208.png',
      'icons/apple-launch-1242x2688.png',
      'icons/apple-launch-1536x2048.png',
      'icons/apple-launch-1668x2224.png',
      'icons/apple-launch-1668x2388.png',
      'icons/apple-launch-2048x2732.png',
    ]

    // Check which Icon Genie files actually exist
    const generatedFiles = []
    for (const file of expectedIconGenieFiles) {
      const fullPath = path.join(rootDir, 'public', file)
      if (await fs.pathExists(fullPath)) {
        generatedFiles.push(file)
      }
    }

    // Report results
    if (missingFiles.length > 0) {
      console.warn(
        '\n   ⚠️  Missing icon/splash files referenced in index.html:'
      )
      missingFiles.forEach((file) => console.warn(`      - ${file}`))
      console.warn(
        '\n   Run "npx icongenie generate -m pwa" to generate missing files\n'
      )
    }

    // Check if index.html is missing references to generated files
    const referencedPaths = foundFiles.concat(missingFiles)
    const unreferencedFiles = generatedFiles.filter(
      (file) => !referencedPaths.includes(file)
    )

    if (unreferencedFiles.length > 0) {
      console.warn(
        '\n   ⚠️  Generated icon files not referenced in index.html:'
      )
      unreferencedFiles.forEach((file) => console.warn(`      - ${file}`))
      console.warn(
        '\n   Consider adding these to index.html for better PWA support\n'
      )
    }

    if (missingFiles.length === 0 && unreferencedFiles.length === 0) {
      console.log(
        '   ✅ All icon and splash screen references verified successfully'
      )
    } else {
      console.log(
        `   ℹ️  Found ${foundFiles.length} valid references, ${missingFiles.length} missing files, ${unreferencedFiles.length} unreferenced files`
      )
    }

    // Return verification status
    return {
      foundFiles,
      generatedFiles,
      missingFiles,
      success: missingFiles.length === 0,
      unreferencedFiles,
    }
  } catch (error) {
    console.error(
      '   ❌ Failed to verify icon references:',
      error instanceof Error ? error.message : String(error)
    )
    throw error
  }
}

// Run the script
makeTenantConfig()
