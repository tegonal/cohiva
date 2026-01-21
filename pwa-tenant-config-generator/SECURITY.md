## Dependency Resolutions (Yarn)

We use Yarn `resolutions` to patch transitive dependency vulnerabilities
when upstream packages have not yet released fixes.

### Current overrides

- **glob → ^10.5.0**
  - CVE: CVE-2025-64756
  - Remove when: pwa-asset-generator > 8.1.2

- **tar → ^7.5.4**
  - CVE: CVE-2025-64118, CVE-2026-23745
  - Remove when: tsx > 4.21.0

- **js-yaml → ^4.1.1**
  - CVE: CVE-2025-64718
  - Remove when: eslint > 9.39.2

- **undici → ^7.18.2**
  - CVE: CVE-2026-22036
  - Remove when: pwa-asset-generator > 8.1.2
