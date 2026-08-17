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

### tsx > 4.23.0

- tar ^7.5.16

### pwa-asset-generator > 8.1.5

- minimatch ^10.2.3
- "ws": "^8.21.0"
- "undici": "^7.28.0"
- "js-cookie": "^3.0.7"
