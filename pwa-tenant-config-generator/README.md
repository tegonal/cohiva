# PWA Tenant Config Generator

Generates tenant-specific PWA assets from config files (settings, theme, logos).

## Quick Start

```bash
corepack enable
yarn install
yarn generate --config-dir tenant-configs/my-tenant
```

## Creating a Tenant Config

```bash
# Copy example as starting point
mkdir -p tenant-configs/my-tenant
cp -r example-config/* tenant-configs/my-tenant/

# Edit config files
cd tenant-configs/my-tenant
# - settings.ts: App name, API endpoints, OAuth client ID
# - theme.ts: Colors (primary, secondary, dark)
# - schemas.ts: API schemas
# - Replace logo.svg, logo-dark.svg, app-icon.svg

# Generate assets
cd ../..
yarn generate --config-dir tenant-configs/my-tenant
```

## Required Input Files

```
tenant-configs/my-tenant/
├── settings.ts       # Site name, domain, OAuth ID
├── theme.ts          # Colors (Quasar variables)
├── schemas.ts        # API schemas
├── logo.svg          # Light mode logo
├── logo-dark.svg     # Dark mode logo
└── app-icon.svg      # App icon (generates 89+ sizes)
```

**Optional**:

- `fonts/` - Custom web fonts (WOFF2)
- `webfonts.scss` - Font-face declarations
- `override.scss` - Custom styles

## Generated Output

Creates `tenant-configs/my-tenant/overlay/`:

```
overlay/
├── pwa-meta.ts              # Meta tags for Quasar template
├── pwa-meta-tags.html       # Raw HTML snippet
├── src/
│   ├── assets/              # Optimized logos
│   └── css/                 # Theme SCSS
├── src-pwa/
│   └── manifest.json        # PWA manifest
└── public/
    └── icons/               # 89+ icons (all iOS/Android sizes)
```

## Key Peculiarities

### 1. Icon Generation Source Priority

- Uses `app-icon.svg` if present
- Falls back to `logo.svg` if no app-icon
- Must be at least 1024x1024px for PNG
- **Icons should include appropriate padding** - no additional padding is added during resize

### 2. pwa-asset-generator Integration

- Generates all iOS/Android sizes
- Creates both light and dark splash screens
- Requires `backgroundColor` in theme.ts

### 3. Template System

- Generates `pwa-meta.ts` with all icon/splash `<link>` tags
- Imported by `quasar.config.ts` as `htmlVariables.pwaMetaTags`
- Injected into `index.html` at build time via `<%- pwaMetaTags %>`

### 4. Validation

- Input: Validates settings/theme against Zod schemas before generation
- Output: Verifies all required files exist after generation
- Fails fast with detailed error messages

## Integration with PWA

The generated config is mounted in Docker and copied at container startup:

```bash
docker run -v /path/to/tenant-configs/my-tenant:/app/tenant-config:ro cohiva-pwa
```

## Troubleshooting

**Validation fails**

- Check settings.ts/theme.ts match example-config structure
- Ensure colors are valid hex (#RRGGBB)
- Verify OAuth client ID is set

**Missing overlay files**

- Check write permissions in config directory
- Ensure all required input files exist
- Review terminal output for pwa-asset-generator errors

**Icon generation fails**

- Verify app-icon.svg is at least 1024x1024px
- Check SVG is valid (no embedded images)
- Ensure icon includes appropriate padding (10-15% recommended) - no padding is added automatically
