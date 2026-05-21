## Dependency Resolutions (Yarn)

We use Yarn `resolutions` to patch transitive dependency vulnerabilities
when upstream packages have not yet released fixes.

### Current overrides

- **flatted → ^3.4.2**
  - CVE: CVE-2026-33228
  - Try removing when: eslint>9.39.4

- **tar → ^7.5.11**
  - CVE: CVE-2026-31802
  - Try removing when: tsx > 4.21.0

- **ip-address → ^10.1.1**
  - CVE: CVE-2026-42338
  - Remove when: pwa-asset-generator > 8.1.2

- **minimatch → ^10.2.3**
  - CVE: CVE-2026-27903
  - Remove when: pwa-asset-generator > 8.1.4
