## Dependency Resolutions (Yarn)

We use Yarn `resolutions` to patch transitive dependency vulnerabilities
when upstream packages have not yet released fixes.

### Current overrides

- **js-yaml → ^4.1.1**
  - CVE: CVE-2025-64718
  - Remove when: eslint > 9.39.2

- **basic-ftp → ^5.2.0**
  - CVE: CVE-2026-27699
  - Remove when: pwa-asset-generator > 8.1.2

- **minimatch → ^9.0.7**
  - CVE: CVE-2026-27903
  - Remove when: pwa-asset-generator > 8.1.2
