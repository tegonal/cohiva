# Cohiva PWA

Progressive Web App for Cohiva - Housing Cooperative Management

## Prerequisites

This project uses **Yarn 4** with Corepack. Enable it first:

```bash
corepack enable
```

**Node.js**: Version 22+ required (see package.json engines field)

## Quick Start

```bash
# 1. Install dependencies
yarn install

# 2. Generate tenant configuration
yarn make:tenant-config

# 3. Start development server with config watching
yarn dev:watch
```

## Development Commands

### Core Development
```bash
# Standard development server (http://localhost:9000)
yarn dev

# Development with automatic config rebuilding (recommended)
yarn dev:watch

# Run config watcher separately
yarn watch:config
```

### Code Quality
```bash
# Run ESLint
yarn lint
yarn lint:fix

# Format with Prettier
yarn format
yarn format:check

# Run both linting and formatting
yarn check
```

### Testing
```bash
# Run tests (not yet implemented)
yarn test
```

## Build & Deployment

### Production Build
```bash
# Build PWA (includes tenant config generation)
yarn build
# or
yarn build:pwa

# Test production build locally (http://localhost:4000)
yarn serve

# NOTE: For API access during local testing, add localhost:4000 
# to CORS_ALLOWED_ORIGINS in Django backend
```

### Tenant Configuration
```bash
# Generate all tenant-specific assets and styles
yarn make:tenant-config

# This processes files from config/ directory:
# - settings.js (deployment config)
# - theme.js (colors)
# - icon.svg & logo.svg (branding)
# - webfonts.scss & fonts/ (typography)
# - override.scss (custom styles)
```

See [config/README.md](config/README.md) for detailed configuration guide.

## Project Structure

```
pwa/
├── config/             # Tenant configuration (customize per deployment)
│   ├── settings.js     # App settings
│   ├── theme.js        # Color theme
│   ├── icon.svg        # App icon
│   ├── logo.svg        # Brand logo
│   ├── webfonts.scss   # Font definitions
│   ├── override.scss   # Style overrides
│   └── fonts/          # Font files
├── src/
│   ├── boot/          # App initialization
│   ├── components/    # Vue components
│   ├── layouts/       # Page layouts
│   ├── pages/         # Route pages
│   ├── router/        # Vue Router config
│   ├── stores/        # Pinia state management
│   ├── i18n/          # Translations (German only)
│   └── css/           # Generated styles (git-ignored)
├── src-pwa/           # PWA service worker
├── public/            # Static files
│   └── icons/         # Generated PWA icons (git-ignored)
└── scripts/           # Build scripts
    ├── make-tenant-config.js   # Config processor
    ├── watch-config.js         # Config watcher
    └── download-roboto.js      # Font downloader
```

## Configuration System

The app uses a **tenant configuration system** that allows complete customization without code changes:

1. **Required Files** in `config/`:
   - `settings.js` - Deployment settings
   - `theme.js` - Visual theme
   - `icon.svg` - App icon (16x16 to 512x512)
   - `logo.svg` - Brand logo (splash screens)

2. **Optional Files**:
   - `webfonts.scss` - Custom fonts
   - `override.scss` - Style overrides
   - `fonts/` - Font files (Roboto included by default)

3. **Generated Files** (git-ignored):
   - `/src/css/app.scss` - Theme styles
   - `/src/css/webfonts.scss` - Font definitions
   - `/src/css/override.scss` - Custom styles
   - `/src-pwa/manifest.json` - PWA manifest
   - `/public/icons/*` - All PWA icons

## Maintenance Commands

### Package Management
```bash
# Check for outdated packages
yarn outdated

# Interactive upgrade
yarn up

# Upgrade Quasar packages
yarn upgrade
yarn upgrade:install

# Prepare Quasar framework
yarn prepare
```

### Icon Generation
```bash
# Generate PWA icons from config/icon.svg and config/logo.svg
yarn icon:generate

# Verify generated icons
yarn icon:verify
```

## Technology Stack

- **Framework**: [Quasar v2](https://quasar.dev/) (Vue 3)
- **State Management**: Pinia
- **Router**: Vue Router 4 (hash mode)
- **HTTP Client**: Axios
- **UI Components**: Quasar Components + Material Icons
- **Internationalization**: vue-i18n (German only)
- **PWA**: Workbox service workers
- **Build Tool**: Vite
- **Package Manager**: Yarn 4
- **Code Quality**: ESLint, Prettier

## Environment Configuration

The app determines API endpoints based on development/production mode:

- **Development**: Uses proxy `/api-proxy/` (configured in quasar.config.js)
- **Production**: Uses settings from `config/settings.js`

## Important Notes

1. **Automated Configuration**: No manual file copying needed. The `make:tenant-config` script handles all configuration processing.

2. **Generated Files**: All generated files are git-ignored. Only modify files in `config/` directory.

3. **Icon Generation**: Icons are automatically generated from `config/icon.svg` and `config/logo.svg` using Icon Genie.

4. **Font System**: Roboto fonts are included by default in `config/fonts/`. Custom fonts can be added there.

5. **German UI**: Currently, the interface is only available in German.

6. **Token Auth**: Uses token-based authentication, not sessions.

## Deployment

### CI/CD Pipeline
```bash
# 1. Copy tenant-specific config
cp -r tenant-configs/${TENANT}/config/* ./config/

# 2. Build with tenant configuration
yarn build

# 3. Deploy dist/pwa/ directory
```

### Docker Support
Dockerfile available for containerized deployments (see project root).

## Troubleshooting

### Build Issues
- Run `yarn make:tenant-config` manually to see errors
- Check all required files exist in `config/`
- Verify Icon Genie is installed: `yarn add -D @quasar/icongenie`

### Development Server
- Default port: 9000
- If port is busy, Quasar will auto-increment
- API proxy configured for development to avoid CORS

### Production Testing
- Serve locally with `yarn serve`
- Add `localhost:4000` to Django's CORS_ALLOWED_ORIGINS
- Check browser console for API connection issues

## Contributing

1. Make changes in appropriate directories
2. Run `yarn check` to fix linting/formatting
3. Test with `yarn dev:watch` for immediate feedback
4. Build and test production: `yarn build && yarn serve`

## License

See LICENSE file in project root.

## Legacy Notes

The following instructions are **deprecated** and replaced by the tenant configuration system:

- ~~Manual copying of example files (settings_example.js, etc.)~~
- ~~Direct icon generation with custom paths~~
- ~~Manual logo copying to src/assets~~

Use `yarn make:tenant-config` instead, which handles all configuration automatically.