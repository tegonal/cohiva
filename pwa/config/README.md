# Tenant Configuration System

This directory contains the tenant-specific configuration that customizes the Cohiva PWA for each deployment. All branding, theming, and deployment settings are centralized here.

## Overview

The configuration system allows complete customization of the PWA without modifying source code. Each tenant gets their own branded experience through configuration files that control appearance, assets, and behavior.

## Directory Structure

```
config/
├── settings.js         # Deployment settings (required)
├── theme.js           # Color theme (required)
├── icon.svg           # App icon for small displays (required)
├── logo.svg           # Logo for branding/splash screens (required)
├── webfonts.scss      # Font definitions (optional)
├── override.scss      # Custom style overrides (optional)
└── fonts/             # Web font files (optional)
    ├── *.woff2
    └── *.woff
```

## Required Files

### 1. `settings.js` - Deployment Configuration
Defines environment-specific settings:
- **Hostnames**: Production and test server URLs
- **Branding**: Site name, nickname, description
- **Features**: App-specific configuration
- **Links**: External URLs, contact information

### 2. `theme.js` - Visual Theme
Quasar theme colors that define the app's appearance:
- **Primary colors**: Main brand colors
- **Semantic colors**: Success, warning, error states
- **Background colors**: Page and component backgrounds
- All colors should be hex values (e.g., `#1976D2`)

### 3. `icon.svg` - App Icon
Used for app icons, favicons, and home screen icons:
- **Purpose**: Small, recognizable icon
- **Requirements**: Works well at 16x16px up to 512x512px
- **Format**: SVG with clear shapes, minimal detail
- **Usage**: Taskbar, browser tabs, app stores

### 4. `logo.svg` - Brand Logo
Used for splash screens and larger branding:
- **Purpose**: Full brand representation
- **Requirements**: Minimum 1024x1024px viewport
- **Format**: Can be more detailed than icon
- **Usage**: Splash screens, login pages, about sections

## Optional Files

### 5. `webfonts.scss` - Typography
Defines custom fonts for the application:
- **@font-face declarations**: Links to font files
- **Font variables**: Overrides Quasar's typography
- **Default**: Roboto font family included

### 6. `override.scss` - Style Customizations
Tenant-specific style overrides:
- **Component styling**: Button shapes, shadows, etc.
- **Layout adjustments**: Spacing, sizing
- **Additional CSS**: Any custom styles
- **Loaded last**: Ensures overrides take precedence

### 7. `fonts/` Directory - Font Files
Contains actual font files:
- **Formats**: WOFF2 (preferred), WOFF
- **Organization**: All font weights/styles
- **Default included**: Roboto family (300, 400, 500, 700)

## Build Process

The `make-tenant-config.js` script processes these files during build:

1. **Asset Generation**
   - Converts icon/logo SVG to PNG if needed
   - Generates all PWA icons via Icon Genie
   - Creates favicons and splash screens

2. **File Distribution**
   - Copies icon/logo to `src/assets/`
   - Copies fonts to `src/css/fonts/`
   - Generates `src/css/app.scss` with theme
   - Copies overrides to `src/css/override.scss`

3. **Manifest Creation**
   - Generates `src-pwa/manifest.json`
   - Sets app name, colors, icons
   - Configures PWA properties

## Development Workflow

### Manual Build
```bash
# Generate tenant configuration
yarn run make:tenant-config

# Build the app
yarn run build
```

### Development with Auto-Reload
```bash
# Watch config files and auto-rebuild on changes
yarn run dev:watch
```

### Standalone Config Watcher
```bash
# Just watch config files (useful for testing)
yarn run watch:config
```

## Deployment Strategies

### 1. Multi-Tenant Repository
Store configurations for all tenants:
```
tenant-configs/
├── tenant1/
│   └── config/
├── tenant2/
│   └── config/
└── tenant3/
    └── config/
```

### 2. CI/CD Pipeline Integration
Replace config during build:
```bash
# Copy tenant-specific config
cp -r deployments/$TENANT/config/* ./config/

# Build with tenant config
yarn run build
```

### 3. Environment Variables
Select configuration based on environment:
```bash
TENANT=customer1 yarn run build
```

## File Size Guidelines

- **Icons**: SVG preferred, PNG minimum 1024x1024
- **Fonts**: WOFF2 format (~15-20KB per weight)
- **Total config**: Keep under 1MB for fast builds

## Validation Checklist

Before deployment, ensure:
- [ ] All required files present (settings, theme, icon, logo)
- [ ] SVG files valid and proper dimensions
- [ ] Theme colors in correct hex format
- [ ] Settings URLs match deployment environment
- [ ] Fonts load correctly (if custom)
- [ ] Override styles don't break layouts

## Default Configuration

The repository includes a complete default configuration:
- **Cohiva Demo** branding
- **Blue theme** (#1976D2 primary)
- **Roboto fonts** (all weights)
- **Example overrides** (commented out)

This default serves as both a working example and fallback configuration.

## Troubleshooting

### Icons not generating
- Check SVG files are valid
- Ensure Icon Genie is installed: `yarn add -D @quasar/icongenie`
- Verify minimum resolution (1024x1024)

### Fonts not loading
- Check file paths in webfonts.scss
- Verify font files exist in config/fonts/
- Ensure WOFF2/WOFF format

### Styles not applying
- Check override.scss syntax
- Verify CSS specificity
- Use `!important` sparingly when needed

### Build failures
- Run `yarn run make:tenant-config` manually
- Check console for specific errors
- Verify all required files present

## Important Notes

1. **No source code changes needed** - Everything configurable via this directory
2. **Generated files are git-ignored** - Only config/ is version controlled
3. **Hot reload in development** - Config changes auto-rebuild with watcher
4. **Icon Genie generates fixed set** - 31 files for PWA (icons + splashscreens)
5. **Fonts are self-hosted** - No external CDN dependencies
