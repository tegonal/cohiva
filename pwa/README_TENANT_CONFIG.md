# Tenant Configuration Guide

Tenant configurations contain branding, theming, settings, and generated assets for each deployment.

## Prerequisites

This guide assumes you have the full Cohiva monorepo checked out:
```
cohiva/
├── pwa/                           # This project
└── pwa-tenant-config-generator/   # Config generator (required)
```

## Development Setup

### First Time

```bash
cd pwa
yarn install
yarn dev  # Auto-generates example config if missing
```

The `pwa/tenant-config/` directory is gitignored - configs are tenant-specific and generated from `pwa-tenant-config-generator`.

### Creating a New Tenant Config

```bash
cd pwa-tenant-config-generator
mkdir -p tenant-configs/my-tenant
cp -r example-config/* tenant-configs/my-tenant/
```

Edit the config files:
- `settings.ts` - App name, API endpoints, OAuth client ID
- `theme.ts` - Colors (primary, secondary, dark)
- `schemas.ts` - API schemas
- `app-icon.svg` - Source icon (generates all sizes)
- `logo.svg`, `logo-dark.svg` - Logos for light/dark mode
- `fonts/`, `override.scss`, `webfonts.scss` - Optional customization

Generate assets:

```bash
cd pwa-tenant-config-generator
yarn generate --config-dir tenant-configs/my-tenant
```

This creates `tenant-configs/my-tenant/overlay/` with:
- 89+ icons and splash screens (all iOS/Android sizes)
- PWA manifest, optimized logos, theme CSS
- `pwa-meta.ts` - Meta tags imported by Quasar

Test locally:

```bash
cd pwa

# Option 1: One-time copy
tsx scripts/setup-dev-config.ts --config-dir ../pwa-tenant-config-generator/tenant-configs/my-tenant
yarn dev

# Option 2: Watch mode (auto-regenerates on source changes)
yarn dev:tenant ../pwa-tenant-config-generator/tenant-configs/my-tenant
```

## Production Deployment

### Critical Requirements

1. **Pre-generate assets**: Run `yarn generate` in pwa-tenant-config-generator before deployment
2. **Mount at `/app/tenant-config`**: Volume path is hardcoded
3. **Mount entire tenant config directory**: Container requires all config files (settings.ts, theme.ts, schemas.ts) and the overlay/ directory

### Docker Compose

```yaml
services:
  pwa-my-tenant:
    image: cohiva-pwa:latest
    ports:
      - "4000:4000"
    volumes:
      - /path/to/pwa-tenant-config-generator/tenant-configs/my-tenant:/app/tenant-config:ro
```

### Docker Run

```bash
docker run -d \
  --name pwa-my-tenant \
  -p 4000:4000 \
  -v /path/to/pwa-tenant-config-generator/tenant-configs/my-tenant:/app/tenant-config:ro \
  cohiva-pwa:latest
```

### What Happens at Startup

The container:
1. Validates `/app/tenant-config/overlay/` exists
2. Copies overlay assets to `/app/src/`, `/app/src-pwa/`, `/app/public/`
3. Builds PWA (~1-2 minutes)
4. Serves on port 4000

**Important**: PWA builds at container startup, not image build time.

## How It Works

### Template System

Quasar injects config values into `index.html` at build time:

```typescript
// quasar.config.ts
import { pwaMetaTags } from './tenant-config/overlay/pwa-meta'
import { settings } from './tenant-config/settings'
import theme from './tenant-config/theme'

htmlVariables: {
  productName: settings.siteName,
  themeColor: theme.primary,
  pwaMetaTags,  // All icon/splash <link> tags
}
```

```html
<!-- index.html -->
<meta name="theme-color" content="<%= themeColor %>" />
<%- pwaMetaTags %>
```

### Directory Structure

Mount this structure at `/app/tenant-config`:

```
tenant-configs/my-tenant/
├── settings.ts, theme.ts, schemas.ts
├── app-icon.svg, logo.svg, logo-dark.svg
├── fonts/, override.scss, webfonts.scss (optional)
└── overlay/                    # Required!
    ├── pwa-meta.ts
    ├── src/assets/*.svg
    ├── src/css/*.scss
    ├── src-pwa/manifest.json
    └── public/icons/*.png (89+ files)
```

## Troubleshooting

**Container fails to start**
```bash
# Check volume is mounted
docker exec container ls /app/tenant-config/overlay

# Check logs
docker logs container
```

**Missing pwa-meta.ts import error**
```bash
yarn setup:dev-config
```

**Config not updating in dev**
```bash
rm -rf tenant-config/overlay && yarn dev
```
