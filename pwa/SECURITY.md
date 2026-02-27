## Dependency Resolutions (Yarn)

We use Yarn `resolutions` to patch transitive dependency vulnerabilities
when upstream packages have not yet released fixes.

### Current overrides

- **qs → ^6.14.2**
  - CVE: CVE-2025-15284, CVE-2026-2391
  - Remove when: @quasar/app-vite > 2.4.1 and/or @quasar/cli@npm > 2.5.0 ??

- **js-yaml → ^4.1.1**
  - CVE: CVE-2025-64718
  - Remove when: eslint > 9.39.2

- **minimatch → ^10.2.3**
  - CVE: CVE-2026-27903
  - Remove when: pworkbox-build > 7.4.0

- **rollup → ^4.59.0**
  - CVE: CVE-2026-27606
  - Remove when: @quasar/app-vite > 2.4.1
