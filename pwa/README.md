# Cohiva App

Bewohnenden-App von Cohiva

## Initial framework installation and app creation

```bash
yarn global add @quasar/cli
yarn create quasar
```

Install [Icon Genie](https://quasar.dev/icongenie/installation) for icon generation:

```bash
yarn global add @quasar/icongenie
```

## Install the dependencies

```bash
yarn
# or
npm install
```

### Start the app in development mode (hot-code reloading, error reporting, etc.)

```bash
quasar dev
```

### Lint the files

```bash
yarn lint
# or
npm run lint
```

### Format the files

```bash
yarn format
# or
npm run format
```

### Build the app for production

```bash
quasar build -m pwa  ## For PWA mode
```

Test production build locally with quasar web server:
(NOTE: You have to add localhost:4000 to `CORS_ALLOWED_ORIGINS` to make that work with the production API.)

```bash
quasar serve dist/pwa/
```

### Customize the configuration

Copy and adjust config files to customize the Cohiva app:

```bash
cp settings_example.js settings.js
cp package_example.json package.json
cp src-pwa/manifest_example.json src-pwa/manifest.json
cp src/css/app_example.scss src/css/app.scss
## Adjust names/settings in the files.
```

Copy/link custom logo to `src/assets/logo.svg`.

Create custom icons in `public` from source icon file (see [docs](https://quasar.dev/icongenie/command-list) for options):

```bash
icongenie generate -i src/assets/icon_example.png [--skip-trim]
icongenie verify
```

See [Configuring quasar.config.js](https://v2.quasar.dev/quasar-cli-vite/quasar-config-js) for Quasar framework settings.

## Update/manage node and dependencies

Install n as node package manager:

```bash
yarn global add n  ## if not installed already
n lst ## Install latest node LTS
n  ## Switch node version
```

Upgrade quasar packages:

```bash
quasar upgrade [-i]
```

List / Upgrade project dependencies:

```bash
yarn outdated
yarn upgrade [--latest] ## --latest will also do backward-incompatible updates
```
