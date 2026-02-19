## Dependency Resolutions (Yarn)

We use Yarn `resolutions` to patch transitive dependency vulnerabilities
when upstream packages have not yet released fixes.

### Current overrides

- **js-yaml → ^4.1.1**
  - CVE: CVE-2025-64718
  - Remove when: eslint > 9.39.2
