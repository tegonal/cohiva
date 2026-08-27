# How to do security updates?

0. Show dependency and installed version(s)

   yarn why -R <package>

1. Try to update direct dependency

   yarn up <direct dependency>

2. Check if package has been updated to the required version. If not, add it to `resolutions` in `package.json` and add it to the list below for later removal.

3. Install new resolutions with

   yarn install

# Dependency Resolutions (Yarn)

We use Yarn `resolutions` to patch transitive dependency vulnerabilities
when upstream packages have not yet released fixes.

## Current overrides

Try to remove the listed packages from `resolutions` in `package.json`
when the following packages have been updated:

### eslint > 9.39.4

- "flatted": "^3.4.2",
- "js-yaml": "^4.3.0"

### @quasar/app-vite > 2.6.0

- tar ^7.5.22
- lodash ^4.18.0
- minimatch ^10.2.3
- picomatch ^4.0.4
- ip-address ^10.5.0
- vite ^8.0.16
- postcss ^8.5.23
- immutable ^5.1.8

### @quasar/cli > 4.0.0

- follow-redirects ^1.16.0

### workbox-build > 7.4.1

- @babel/helper-module-transforms ^7.29.4
- fast-uri ^3.1.5

### @intlify/unplugin-vue-i18n > 11.2.5

- "brace-expansion": "^5.0.9"
