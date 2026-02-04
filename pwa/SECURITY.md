## Dependency Resolutions (Yarn)

We use Yarn `resolutions` to patch transitive dependency vulnerabilities
when upstream packages have not yet released fixes.

### Current overrides

- **qs → ^6.14.1**
  - CVE: CVE-2025-15284
  - Remove when: @quasar/app-vite > 2.4.0

- **node-forge → ^1.3.2**
  - CVE: CVE-2025-12816
  - Remove when: @quasar/app-vite > 2.4.0

- **vite → ^7.1.11**
  - CVE: CVE-2025-62522
  - Remove when: @quasar/app-vite > 2.4.0

- **glob → ^10.5.0**
  - CVE: CVE-2025-64756
  - Remove when: @quasar/app-vite > 2.4.0

- **tar → ^7.5.7**
  - CVE: CVE-2025-64118, CVE-2026-23745, CVE-2026-24842
  - Remove when: @quasar/app-vite > 2.4.0

- **js-yaml → ^4.1.1**
  - CVE: CVE-2025-64718
  - Remove when: eslint > 9.39.2

- **lodash → ^4.17.23**
  - CVE: CVE-2025-13465
  - Remove when: @quasar/app-vite > 2.4.0
