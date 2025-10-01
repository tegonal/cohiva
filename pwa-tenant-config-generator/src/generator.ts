/**
 * Tenant Configuration Generator
 *
 * Generates all tenant-specific assets and configuration files
 * into <config-dir>/overlay/
 */

import { exec } from 'child_process'
import fs from 'fs-extra'
import path from 'path'
import sharp from 'sharp'
import { optimize } from 'svgo'
import { promisify } from 'util'

import { validateSettings, validateTheme } from './schemas.js'

const execAsync = promisify(exec)

// Minimum resolution for PWA assets (Icon Genie requirement)
const MIN_ICON_SIZE = 1024

interface GeneratorOptions {
  configDir: string
  outputDir: string
}

interface TenantConfig {
  settings: any
  theme: any
}

/**
 * Main entry point for tenant config generation
 */
export async function generateTenantConfig(configDir: string): Promise<void> {
  const absoluteConfigDir = path.resolve(configDir)
  const outputDir = path.join(absoluteConfigDir, 'overlay')

  console.log('Generating tenant configuration...')
  console.log(`   Config directory: ${absoluteConfigDir}`)
  console.log(`   Output directory: ${outputDir}`)
  console.log('')

  const options: GeneratorOptions = {
    configDir: absoluteConfigDir,
    outputDir,
  }

  try {
    // Clean output directory
    await fs.remove(outputDir)
    await fs.ensureDir(outputDir)

    // Load and validate configuration
    const config = await loadAndValidateConfig(options)

    // Generate all assets
    await generateAssets(options, config)

    // Validate generated output
    await validateGeneratedConfig(options)

    console.log('')
    console.log('Tenant configuration generated and validated successfully!')
    console.log(`   Output: ${outputDir}`)
  } catch (error) {
    console.error('Generation failed:', error)
    throw error
  }
}

/**
 * Check if image meets minimum resolution requirements
 */
async function checkImageResolution(imagePath: string): Promise<boolean> {
  try {
    const metadata = await sharp(imagePath).metadata()
    if (!metadata.width || !metadata.height) return false
    return metadata.width >= MIN_ICON_SIZE && metadata.height >= MIN_ICON_SIZE
  } catch {
    return false
  }
}

/**
 * Convert SVG to PNG at specified resolution
 */
async function convertSvgToPng(
  svgPath: string,
  outputPath: string,
  size = MIN_ICON_SIZE
): Promise<string> {
  console.log(`   Converting SVG to PNG (${size}x${size})...`)

  const svgBuffer = await fs.readFile(svgPath)

  await sharp(svgBuffer)
    .resize(size, size, {
      background: { alpha: 0, b: 0, g: 0, r: 0 },
      fit: 'contain',
    })
    .png()
    .toFile(outputPath)

  console.log('   PNG created')
  return outputPath
}

/**
 * Generate additional standard icon sizes not created by pwa-asset-generator
 * pwa-asset-generator only creates 192 and 512, we need 32, 128, 256, 384
 * Note: Icons are resized without padding - source icons should already include appropriate padding
 */
async function generateAdditionalIconSizes(
  sourcePath: string,
  outputDir: string,
  backgroundColor: string
): Promise<void> {
  console.log('   Generating additional icon sizes (32, 128, 256, 384)...')

  const iconSizes = [32, 128, 256, 384]
  const faviconSizes = [32] // Sizes to also save as favicon-{size}.png

  // Parse background color
  const bg = backgroundColor.match(/^#([0-9a-f]{6})$/i)
  const bgColor = bg
    ? {
        alpha: 1,
        b: parseInt(bg[1].substring(4, 6), 16),
        g: parseInt(bg[1].substring(2, 4), 16),
        r: parseInt(bg[1].substring(0, 2), 16),
      }
    : { alpha: 1, b: 255, g: 255, r: 255 }

  for (const size of iconSizes) {
    const outputPath = path.join(outputDir, `manifest-icon-${size}.png`)

    // Resize without padding - source icon should already include appropriate padding
    const buffer = await sharp(sourcePath)
      .flatten({ background: bgColor })
      .resize(size, size, {
        background: bgColor,
        fit: 'contain',
      })
      .png()
      .toBuffer()

    // Save as manifest-icon
    await fs.writeFile(outputPath, buffer)

    // Also save as favicon for specific sizes
    if (faviconSizes.includes(size)) {
      const faviconPath = path.join(outputDir, `favicon-${size}.png`)
      await fs.writeFile(faviconPath, buffer)
    }
  }

  console.log('   Additional icon sizes created')
}

/**
 * Generate all assets and configuration files
 */
async function generateAssets(
  options: GeneratorOptions,
  config: TenantConfig
): Promise<void> {
  // 1. Setup logos
  await setupLogos(options)

  // 2. Generate PWA icons and splash screens
  const { iconMetaTags, splashMetaTags } = await generatePWAAssets(
    options,
    config
  )

  // 3. Generate social media cards
  await generateSocialCards(options, config)

  // 4. Generate manifest.json
  await generateManifest(options, config)

  // 5. Generate PWA meta tags snippet
  const pwaMetaTags = await generatePwaMetaSnippet(options, {
    iconMetaTags,
    splashMetaTags,
  })

  // 6. Setup fonts
  await setupFonts(options)

  // 7. Generate SCSS files
  await generateStyles(options, config)

  // 8. Generate pwa-meta.ts config file
  await generatePwaMetaConfig(options, pwaMetaTags)
}

/**
 * Generate manifest.json
 */
async function generateManifest(
  options: GeneratorOptions,
  config: TenantConfig
): Promise<void> {
  console.log('Generating manifest.json...')

  const manifest = {
    background_color: config.theme.backgroundColor,
    description:
      config.settings.siteDescription ||
      `${config.settings.siteName} Progressive Web App`,
    display: 'standalone',
    icons: [
      // Standard icons (any purpose - used by browsers, iOS, etc.)
      {
        purpose: 'any',
        sizes: '128x128',
        src: 'icons/manifest-icon-128.png',
        type: 'image/png',
      },
      {
        purpose: 'any',
        sizes: '192x192',
        src: 'icons/manifest-icon-192.png',
        type: 'image/png',
      },
      {
        purpose: 'any',
        sizes: '256x256',
        src: 'icons/manifest-icon-256.png',
        type: 'image/png',
      },
      {
        purpose: 'any',
        sizes: '384x384',
        src: 'icons/manifest-icon-384.png',
        type: 'image/png',
      },
      {
        purpose: 'any',
        sizes: '512x512',
        src: 'icons/manifest-icon-512.png',
        type: 'image/png',
      },
      // Maskable icons (for Android adaptive icons)
      {
        purpose: 'maskable',
        sizes: '192x192',
        src: 'icons/manifest-icon-192.maskable.png',
        type: 'image/png',
      },
      {
        purpose: 'maskable',
        sizes: '512x512',
        src: 'icons/manifest-icon-512.maskable.png',
        type: 'image/png',
      },
    ],
    id: `/${config.settings.appBasename}/`,
    name: config.settings.siteName,
    orientation: 'portrait',
    short_name: config.settings.siteNickname,
    start_url: '/',
    theme_color: config.theme.primary,
  }

  const manifestDir = path.join(options.outputDir, 'src-pwa')
  await fs.ensureDir(manifestDir)
  await fs.writeJson(path.join(manifestDir, 'manifest.json'), manifest, {
    spaces: 2,
  })

  console.log('   manifest.json created')
}

/**
 * Generate PWA icons and splash screens using pwa-asset-generator
 * Returns HTML meta tags for icons and splash screens
 */
async function generatePWAAssets(
  options: GeneratorOptions,
  config: TenantConfig
): Promise<{ iconMetaTags: string; splashMetaTags: string }> {
  console.log('Generating PWA assets...')

  // Determine icon source
  const iconSourcePath = await prepareIconSource(options)

  const publicDir = path.join(options.outputDir, 'public')
  const iconsDir = path.join(publicDir, 'icons')
  await fs.ensureDir(iconsDir)

  // Get background colors from theme
  const iconBackgroundColor = config.theme.backgroundColor
  const splashBackgroundColor = config.theme.splashBackgroundColor

  // Get the path to pwa-asset-generator binary
  const pwaAssetBin = path.join(
    path.dirname(new URL(import.meta.url).pathname),
    '..',
    'node_modules',
    '.bin',
    'pwa-asset-generator'
  )

  // Generate icons with icon background color
  console.log(`   Running pwa-asset-generator (standard icons)...`)

  // Detect CI environment and add --no-sandbox flag if needed
  const isCI = process.env.CI === 'true' || process.env.GITHUB_ACTIONS === 'true'
  const sandboxFlag = isCI ? '-n' : ''

  const iconBaseCmd =
    `"${pwaAssetBin}" "${iconSourcePath}" "${iconsDir}" ` +
    `--background "${iconBackgroundColor}" ` +
    `--opaque true ` +
    `--padding "10%" ` +
    `--type png ` +
    `--favicon ` +
    `--icon-only ` +
    `${sandboxFlag}`

  // Generate standard icons (192, 512) and capture HTML output
  let iconMetaTags = ''
  try {
    const { stdout } = await execAsync(`${iconBaseCmd} --maskable false`)
    // Extract HTML link tags from stdout
    const linkMatches = stdout.match(/<link[^>]*>/g)
    const metaMatches = stdout.match(/<meta[^>]*>/g)

    if (linkMatches) {
      iconMetaTags += linkMatches
        .filter((tag) => tag.includes('apple'))
        .join('\n')
    }
    if (metaMatches) {
      iconMetaTags +=
        '\n' + metaMatches.filter((tag) => tag.includes('apple')).join('\n')
    }
  } catch (error) {
    throw new Error(
      `pwa-asset-generator failed: ${error instanceof Error ? error.message : String(error)}`
    )
  }

  console.log(`   Running pwa-asset-generator (maskable icons)...`)

  // Generate maskable icons (192.maskable, 512.maskable)
  try {
    await execAsync(`${iconBaseCmd} --maskable true`)
  } catch (error) {
    throw new Error(
      `pwa-asset-generator failed: ${error instanceof Error ? error.message : String(error)}`
    )
  }

  // Generate light mode splash screens and capture HTML output
  console.log(`   Running pwa-asset-generator (light splash screens)...`)

  const splashCmd =
    `"${pwaAssetBin}" "${iconSourcePath}" "${iconsDir}" ` +
    `--background "${splashBackgroundColor}" ` +
    `--opaque true ` +
    `--padding "10%" ` +
    `--type png ` +
    `--splash-only ` +
    `--scrape true ` +
    `${sandboxFlag}`

  let splashMetaTags = ''
  try {
    const { stdout } = await execAsync(splashCmd)
    // Extract splash screen link tags
    const linkMatches = stdout.match(
      /<link[^>]*apple-touch-startup-image[^>]*>/g
    )
    if (linkMatches) {
      splashMetaTags = linkMatches.join('\n')
    }
  } catch (error) {
    throw new Error(
      `pwa-asset-generator splash screens failed: ${error instanceof Error ? error.message : String(error)}`
    )
  }

  // Generate dark mode splash screens if logo-dark exists
  const logoDarkPath = path.join(options.configDir, 'logo-dark.svg')
  if (await fs.pathExists(logoDarkPath)) {
    console.log(`   Running pwa-asset-generator (dark splash screens)...`)

    // Convert logo-dark.svg to PNG for splash screens
    const darkIconPath = path.join(options.configDir, '.temp-icon-dark.png')
    await convertSvgToPng(logoDarkPath, darkIconPath)

    // Use dark background if defined, otherwise use splash background
    const darkSplashBg =
      config.theme.darkSplashBackgroundColor ||
      config.theme.splashBackgroundColor

    const darkSplashCmd =
      `"${pwaAssetBin}" "${darkIconPath}" "${iconsDir}" ` +
      `--background "${darkSplashBg}" ` +
      `--opaque true ` +
      `--padding "10%" ` +
      `--type png ` +
      `--splash-only ` +
      `--dark-mode ` +
      `--scrape true ` +
      `${sandboxFlag}`

    try {
      const { stdout } = await execAsync(darkSplashCmd)
      // Extract dark splash screen link tags and append
      const darkLinkMatches = stdout.match(
        /<link[^>]*apple-touch-startup-image[^>]*>/g
      )
      if (darkLinkMatches) {
        splashMetaTags += '\n' + darkLinkMatches.join('\n')
      }
    } catch (error) {
      throw new Error(
        `pwa-asset-generator dark splash screens failed: ${error instanceof Error ? error.message : String(error)}`
      )
    }

    // Clean up temp dark icon
    await fs.remove(darkIconPath)
  }

  console.log('   PWA assets generated')

  // Generate additional standard icon sizes (32, 128, 256, 384) using Sharp
  await generateAdditionalIconSizes(
    iconSourcePath,
    iconsDir,
    iconBackgroundColor
  )

  // Clean up temp icon if created
  const tempIconPath = path.join(options.configDir, '.temp-icon.png')
  if (await fs.pathExists(tempIconPath)) {
    await fs.remove(tempIconPath)
  }

  return { iconMetaTags, splashMetaTags }
}

/**
 * Generate pwa-meta.ts config file with icon/splash meta tags
 */
async function generatePwaMetaConfig(
  options: GeneratorOptions,
  pwaMetaTags: string
): Promise<void> {
  console.log('Generating pwa-meta.ts...')

  // Escape backticks and backslashes in the meta tags string
  const escapedMetaTags = pwaMetaTags
    .replace(/\\/g, '\\\\')
    .replace(/`/g, '\\`')
    .replace(/\$/g, '\\$')

  const content = `// Generated PWA meta tags for icons and splash screens
// This file is auto-generated by pwa-tools - DO NOT EDIT MANUALLY

/**
 * HTML meta tags for PWA icons and splash screens
 * Include this in your index.html <head> section
 */
export const pwaMetaTags = \`${escapedMetaTags}\`
`

  const outputPath = path.join(options.outputDir, 'pwa-meta.ts')
  await fs.writeFile(outputPath, content)
  console.log('   pwa-meta.ts created')
}

/**
 * Generate PWA meta tags snippet for icons and splash screens
 * This snippet should be inserted into the PWA's index.html template
 */
async function generatePwaMetaSnippet(
  options: GeneratorOptions,
  metaTags: { iconMetaTags: string; splashMetaTags: string }
): Promise<string> {
  console.log('Generating PWA meta tags snippet...')

  // Format meta tags with proper indentation and fix paths
  const iconsDir = path.join(options.outputDir, 'public', 'icons')
  const formatMetaTags = (tags: string, indent = 4) => {
    const spaces = ' '.repeat(indent)
    // Replace absolute icons path with relative path (icons/filename)
    const tagsWithRelativePaths = tags.replace(
      new RegExp(iconsDir.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '/', 'g'),
      'icons/'
    )
    return tagsWithRelativePaths
      .split('\n')
      .map((line) => (line.trim() ? spaces + line.trim() : ''))
      .join('\n')
  }

  const iconMetaTagsFormatted = formatMetaTags(metaTags.iconMetaTags, 4)
  const splashMetaTagsFormatted = formatMetaTags(metaTags.splashMetaTags, 4)

  // Generate only the meta tags snippet (no full HTML document)
  const snippet = `    <!-- Favicons and Icons -->
    <link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png" />
    <link rel="icon" type="image/png" sizes="196x196" href="/icons/favicon-196.png" />

    <!-- Apple Touch Icons and Splash Screens -->
${iconMetaTagsFormatted}

${splashMetaTagsFormatted}
`

  await fs.writeFile(
    path.join(options.outputDir, 'pwa-meta-tags.html'),
    snippet
  )
  console.log('   pwa-meta-tags.html snippet created')
  console.log('   [INFO] This snippet will be exported via overlay config')

  return snippet
}

/**
 * Generate social media cards (Open Graph, Twitter)
 */
async function generateSocialCards(
  options: GeneratorOptions,
  config: TenantConfig
): Promise<void> {
  console.log('Generating social media cards...')

  const logoPath = path.join(options.configDir, 'logo.svg')
  const publicDir = path.join(options.outputDir, 'public')
  await fs.ensureDir(publicDir)

  // Parse background color
  const bgColor = config.theme.backgroundColor.replace('#', '')
  const r = parseInt(bgColor.substr(0, 2), 16)
  const g = parseInt(bgColor.substr(2, 2), 16)
  const b = parseInt(bgColor.substr(4, 2), 16)

  const logoBuffer = await fs.readFile(logoPath)

  // Generate Open Graph image (1200x630)
  console.log('   Generating Open Graph image...')
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

  const ogLogoSize = Math.floor(Math.min(1200, 630) * 0.4)
  const ogLogo = await sharp(logoBuffer)
    .resize(ogLogoSize, ogLogoSize, {
      background: { alpha: 0, b, g, r },
      fit: 'contain',
    })
    .png()
    .toBuffer()

  await sharp(ogBackground)
    .composite([{ gravity: 'center', input: ogLogo }])
    .png()
    .toFile(path.join(publicDir, 'og-image.png'))

  console.log('   Open Graph image created')

  // Generate Twitter card (1200x600)
  console.log('   Generating Twitter card...')
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

  const twitterLogoSize = Math.floor(Math.min(1200, 600) * 0.4)
  const twitterLogo = await sharp(logoBuffer)
    .resize(twitterLogoSize, twitterLogoSize, {
      background: { alpha: 0, b, g, r },
      fit: 'contain',
    })
    .png()
    .toBuffer()

  await sharp(twitterBackground)
    .composite([{ gravity: 'center', input: twitterLogo }])
    .png()
    .toFile(path.join(publicDir, 'twitter-card.png'))

  console.log('   Twitter card created')
}

/**
 * Generate SCSS theme files
 */
async function generateStyles(
  options: GeneratorOptions,
  config: TenantConfig
): Promise<void> {
  console.log('Generating SCSS files...')

  const cssDir = path.join(options.outputDir, 'src', 'css')
  await fs.ensureDir(cssDir)

  // Generate quasar.variables.scss
  console.log('   Generating quasar.variables.scss...')
  const skipVars = [
    'backgroundColor',
    'themeColor',
    'splashBackgroundColor',
    'splashIconColor',
  ]

  let scssVariables = ''
  for (const [key, value] of Object.entries(config.theme)) {
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

  await fs.writeFile(
    path.join(cssDir, 'quasar.variables.scss'),
    quasarVariablesContent
  )
  console.log('   quasar.variables.scss created')

  // Generate app.scss
  console.log('   Generating app.scss...')
  const appScssContent = `// Generated from config/theme.ts
// Do not edit directly - modify config/theme.ts instead

// Import web fonts first (this sets font variables)
@import './webfonts.scss';

// Custom app styles
.app-logo {
  height: 40px;
  width: auto;
}

// Additional custom styles can be added below
`

  await fs.writeFile(path.join(cssDir, 'app.scss'), appScssContent)
  console.log('   app.scss created')

  // Copy or create override.scss
  console.log('   Setting up override.scss...')
  const overrideSource = path.join(options.configDir, 'override.scss')
  const overrideTarget = path.join(cssDir, 'override.scss')

  if (await fs.pathExists(overrideSource)) {
    await fs.copy(overrideSource, overrideTarget)
    console.log('   override.scss copied')
  } else {
    await fs.writeFile(overrideTarget, '// No tenant-specific overrides\n')
    console.log('   Empty override.scss created')
  }
}

/**
 * Load and validate configuration files
 */
async function loadAndValidateConfig(
  options: GeneratorOptions
): Promise<TenantConfig> {
  console.log('Loading configuration files...')

  // Load settings (try .ts first, then .js)
  let settingsPath = path.join(options.configDir, 'settings.ts')
  if (!(await fs.pathExists(settingsPath))) {
    settingsPath = path.join(options.configDir, 'settings.js')
  }

  if (!(await fs.pathExists(settingsPath))) {
    throw new Error(
      `settings.ts or settings.js not found in ${options.configDir}`
    )
  }

  const settingsModule = await import(settingsPath)
  const settings = settingsModule.settings

  if (!settings) {
    throw new Error('No settings export found in settings file')
  }

  // Load theme (try .ts first, then .js)
  let themePath = path.join(options.configDir, 'theme.ts')
  if (!(await fs.pathExists(themePath))) {
    themePath = path.join(options.configDir, 'theme.js')
  }

  if (!(await fs.pathExists(themePath))) {
    throw new Error('theme.ts or theme.js not found in config directory')
  }

  const themeModule = await import(themePath)
  const theme = themeModule.default

  if (!theme) {
    throw new Error('No default export found in theme file')
  }

  // Validate
  console.log('   Validating settings...')
  validateSettings(settings)
  console.log('   Settings valid')

  console.log('   Validating theme...')
  validateTheme(theme)
  console.log('   Theme valid')

  return { settings, theme }
}

/**
 * Optimize and copy an SVG file
 */
async function optimizeAndCopySVG(
  sourcePath: string,
  targetPath: string
): Promise<void> {
  const svgContent = await fs.readFile(sourcePath, 'utf8')
  const originalSize = Buffer.byteLength(svgContent, 'utf8')

  try {
    const result = optimize(svgContent, {
      multipass: true,
      path: sourcePath,
      plugins: [
        {
          name: 'preset-default',
          params: {
            overrides: {
              cleanupIds: false,
            },
          },
        },
      ],
    })

    await fs.writeFile(targetPath, result.data)

    const optimizedSize = Buffer.byteLength(result.data, 'utf8')
    const saved = originalSize - optimizedSize
    if (saved > 0) {
      const percent = ((saved / originalSize) * 100).toFixed(1)
      console.log(`     Saved ${percent}% (${saved} bytes)`)
    }
  } catch {
    // If optimization fails, just copy the original
    console.warn('     Warning: SVG optimization failed, copying original')
    await fs.copy(sourcePath, targetPath)
  }
}

/**
 * Prepare icon source file (convert SVG to PNG if needed)
 */
async function prepareIconSource(options: GeneratorOptions): Promise<string> {
  console.log('   Preparing icon source...')

  const iconSvgPath = path.join(options.configDir, 'app-icon.svg')
  const iconPngPath = path.join(options.configDir, 'app-icon.png')
  const logoSvgPath = path.join(options.configDir, 'logo.svg')
  const logoPngPath = path.join(options.configDir, 'logo.png')
  const tempIconPath = path.join(options.configDir, '.temp-icon.png')

  // Check app-icon.png
  if (await fs.pathExists(iconPngPath)) {
    console.log('   Found app-icon.png')
    const isValid = await checkImageResolution(iconPngPath)
    if (isValid) {
      return iconPngPath
    }
    console.log('   Resolution too low, converting from SVG...')
    if (await fs.pathExists(iconSvgPath)) {
      return await convertSvgToPng(iconSvgPath, tempIconPath)
    }
    throw new Error('app-icon.png resolution too low and no app-icon.svg found')
  }

  // Check app-icon.svg
  if (await fs.pathExists(iconSvgPath)) {
    console.log('   Found app-icon.svg, converting to PNG...')
    return await convertSvgToPng(iconSvgPath, tempIconPath)
  }

  // Fallback to logo
  console.log('   No app-icon found, using logo...')
  if (
    (await fs.pathExists(logoPngPath)) &&
    (await checkImageResolution(logoPngPath))
  ) {
    return logoPngPath
  }

  if (await fs.pathExists(logoSvgPath)) {
    return await convertSvgToPng(logoSvgPath, tempIconPath)
  }

  throw new Error('No suitable icon or logo found')
}

/**
 * Setup fonts from config/fonts/
 */
async function setupFonts(options: GeneratorOptions): Promise<void> {
  console.log('Setting up fonts...')

  const fontsSource = path.join(options.configDir, 'fonts')
  const fontsTarget = path.join(options.outputDir, 'src', 'css', 'fonts')
  const webfontsSource = path.join(options.configDir, 'webfonts.scss')
  const webfontsTarget = path.join(
    options.outputDir,
    'src',
    'css',
    'webfonts.scss'
  )

  // Copy fonts directory if it exists
  if (await fs.pathExists(fontsSource)) {
    const fontFiles = await fs.readdir(fontsSource)
    const actualFonts = fontFiles.filter((f) => !f.startsWith('.'))

    if (actualFonts.length > 0) {
      console.log(`   Found ${actualFonts.length} font file(s)`)
      await fs.ensureDir(fontsTarget)
      await fs.copy(fontsSource, fontsTarget)
      console.log('   Fonts copied')
    } else {
      console.log('   No font files found')
    }
  } else {
    console.log('   No fonts directory found')
  }

  // Copy or create webfonts.scss
  if (await fs.pathExists(webfontsSource)) {
    console.log('   Found webfonts.scss')
    await fs.ensureDir(path.dirname(webfontsTarget))
    await fs.copy(webfontsSource, webfontsTarget)
    console.log('   webfonts.scss copied')
  } else {
    console.log('   Creating default webfonts.scss')
    const defaultWebfonts = `// Default web fonts configuration
// Place custom font definitions in config/webfonts.scss

// Default Quasar font family
$typography-font-family: 'Roboto', 'Helvetica Neue', Helvetica, Arial, sans-serif !default;
`
    await fs.ensureDir(path.dirname(webfontsTarget))
    await fs.writeFile(webfontsTarget, defaultWebfonts)
    console.log('   Default webfonts.scss created')
  }
}

/**
 * Copy and optimize logos to overlay/src/assets/
 */
async function setupLogos(options: GeneratorOptions): Promise<void> {
  console.log('Setting up logos...')

  const assetsDir = path.join(options.outputDir, 'src', 'assets')
  await fs.ensureDir(assetsDir)

  // Copy and optimize logo.svg
  const logoSource = path.join(options.configDir, 'logo.svg')
  if (!(await fs.pathExists(logoSource))) {
    throw new Error('logo.svg is required in config directory')
  }
  await optimizeAndCopySVG(logoSource, path.join(assetsDir, 'logo.svg'))
  console.log('   Copied and optimized logo.svg')

  // Copy and optimize logo-dark.svg
  const logoDarkSource = path.join(options.configDir, 'logo-dark.svg')
  if (!(await fs.pathExists(logoDarkSource))) {
    throw new Error('logo-dark.svg is required in config directory')
  }
  await optimizeAndCopySVG(
    logoDarkSource,
    path.join(assetsDir, 'logo-dark.svg')
  )
  console.log('   Copied and optimized logo-dark.svg')
}

/**
 * Validate the generated configuration
 */
async function validateGeneratedConfig(
  options: GeneratorOptions
): Promise<void> {
  console.log('Validating generated configuration...')

  // Check that all required files were generated
  const requiredFiles = [
    'pwa-meta.ts',
    'pwa-meta-tags.html',
    'src/assets/logo.svg',
    'src/assets/logo-dark.svg',
    'src/css/app.scss',
    'src/css/quasar.variables.scss',
    'src/css/webfonts.scss',
    'src/css/override.scss',
    'src-pwa/manifest.json',
    'public/icons/manifest-icon-128.png',
    'public/icons/manifest-icon-192.png',
    'public/icons/manifest-icon-256.png',
    'public/icons/manifest-icon-384.png',
    'public/icons/manifest-icon-512.png',
    'public/icons/manifest-icon-192.maskable.png',
    'public/icons/manifest-icon-512.maskable.png',
    'public/og-image.png',
    'public/twitter-card.png',
  ]

  const missingFiles: string[] = []
  for (const file of requiredFiles) {
    const filePath = path.join(options.outputDir, file)
    if (!(await fs.pathExists(filePath))) {
      missingFiles.push(file)
    }
  }

  if (missingFiles.length > 0) {
    throw new Error(
      `Missing required generated files:\n${missingFiles.map((f) => `  - ${f}`).join('\n')}`
    )
  }

  console.log('   All required files generated')
}
