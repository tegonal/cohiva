# Cohiva PWA

Progressive Web App for housing cooperative management.

## Prerequisites

Requires the full Cohiva monorepo:

```
cohiva/
├── pwa/                           # This project
└── pwa-tenant-config-generator/   # Required for config generation
```

**Node.js**: 24+ required
**Package Manager**: Yarn 4 via Corepack

```bash
corepack enable
```

## Quick Start

```bash
yarn install
yarn dev  # Auto-generates example config if missing
```

Development server runs at http://localhost:9000

## Key Commands

```bash
# Development
yarn dev              # Standard dev server
yarn dev:watch        # Dev server + auto-regenerate local config on changes

# Development with custom tenant config (auto-regenerates on source changes)
yarn dev:tenant ../pwa-tenant-config-generator/tenant-configs/my-tenant

# Build
yarn build            # Production build (validates config first)
yarn serve            # Test production build locally (port 4000)

# Code Quality
yarn lint             # Run linter
yarn check            # Lint + format + type-check
```

## Tenant Configuration

The `tenant-config/` directory is gitignored - configs are deployment-specific and generated from `pwa-tenant-config-generator`.

On first `yarn dev`, the example config is automatically generated and copied to `tenant-config/`.

**See [README_TENANT_CONFIG.md](README_TENANT_CONFIG.md)** for:

- Creating custom tenant configs
- Docker deployment
- Production setup

## Project Structure

```
pwa/
├── tenant-config/      # Gitignored (generated from pwa-tenant-config-generator)
├── src/
│   ├── boot/          # App initialization (axios, i18n, auth)
│   ├── components/    # Vue components
│   ├── pages/         # Route pages
│   ├── stores/        # Pinia stores
│   └── i18n/          # Translations (German only)
├── src-pwa/           # Service worker config
└── scripts/
    ├── setup-dev-config.ts    # Auto-setup on yarn dev
    ├── validate-config.ts     # Zod validation
    └── startup.sh             # Docker entrypoint
```

## Technology Stack

- **Framework**: Quasar v2 (Vue 3 Composition API)
- **State**: Pinia
- **Router**: Vue Router 4 (history mode)
- **Auth**: OAuth2/OIDC (oidc-client-ts)
- **PWA**: Workbox service workers
- **Build**: Vite
- **Code Quality**: ESLint, Prettier, TypeScript

## Important Notes

1. **Monorepo Required**: Must have `pwa-tenant-config-generator/` as sibling directory
2. **Config Validation**: Build fails if settings/theme don't match schemas
3. **German Only**: UI currently only in German
4. **Token Auth**: OAuth2/OIDC, not session-based
5. **CORS for Local Testing**: Add `localhost:4000` to backend's `CORS_ALLOWED_ORIGINS` when testing production builds

## Docker Deployment

See [README_TENANT_CONFIG.md](README_TENANT_CONFIG.md) for production deployment with tenant configs.

## Troubleshooting

**Missing config on first run**

```bash
yarn setup:dev-config
```

**Config validation fails**

- Check `tenant-config/settings.ts` matches schema
- Verify colors in `tenant-config/theme.ts` are valid hex (#RRGGBB)
- Ensure OAuth client ID is set

**Port conflicts**

- Dev server: 9000 (auto-increments if busy)
- Prod server: 4000
