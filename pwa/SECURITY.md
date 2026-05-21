## Dependency Resolutions (Yarn)

We use Yarn `resolutions` to patch transitive dependency vulnerabilities
when upstream packages have not yet released fixes.

### Current overrides

- **flatted → ^3.4.2**
  - CVE: CVE-2026-33228
  - Try removing when: eslint>9.39.4

- **tar → ^7.5.11**
  - CVE: CVE-2026-31802
  - Try removing when: @quasar/app-vite > 2.6.0

- **lodash → ^4.18.0**
  - CVE: CVE-2026-4800
  - Try removing when: @quasar/app-vite > 2.6.0

- **minimatch → ^10.2.3**
  - CVE: CVE-2026-27903
  - Try removing when: @quasar/app-vite > 2.6.0

- **picomatch → ^4.0.4**
  - CVE: CVE-2026-33672
  - Try removing when: @quasar/app-vite > 2.6.0

- **ip-address → ^10.1.1**
  - CVE: CVE-2026-42338
  - Try removing when: @quasar/app-vite > 2.6.0

- **follow-redirects → ^1.16.0**
  - CVE:
  - Try removing when: @quasar/cli > 4.0.0

- **@babel/helper-module-transforms → ^7.29.4**
  - CVE: CVE-2026-44728
  - Try removing when: workbox-build > 7.4.1

- **fast-uri → ^3.1.2**
  - CVE: CVE-2026-6322
  - Try removing when: workbox-build > 7.4.1
