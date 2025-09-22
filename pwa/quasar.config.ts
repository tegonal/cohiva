/* eslint-env node */

/*
 * This file runs in a Node context (it's NOT transpiled by Babel), so use only
 * the ES6 features that are supported by your Node version. https://node.green/
 */

// Configuration for your app
// https://v2.quasar.dev/quasar-cli-vite/quasar-config-js

import { defineConfig } from '#q-app/wrappers'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { settings } from './config/settings'
import theme from './config/theme.js'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

export default defineConfig((ctx) => ({
  // animations: 'all', // --- includes all animations
  // https://v2.quasar.dev/options/animations
  animations: [],

  // https://v2.quasar.dev/quasar-cli/prefetch-feature
  // preFetch: true,

  // app boot file (/src/boot)
  // --> boot files are part of "main.js"
  // https://v2.quasar.dev/quasar-cli/boot-files
  boot: ['i18n', 'axios', 'auth', 'dark-mode'],

  // Full list of options: https://v2.quasar.dev/quasar-cli-vite/quasar-config-js#build
  build: {
    env: {
      API: ctx.dev
        ? 'https://' + settings.testHostname + '.' + settings.domain + '/'
        : 'https://' + settings.prodHostname + '.' + settings.domain + '/',
      API_DIRECT: ctx.dev
        ? 'https://' + settings.testHostname + '.' + settings.domain + '/'
        : 'https://' + settings.prodHostname + '.' + settings.domain + '/',
      OAUTH_CLIENT_ID: settings.oauthClientId,
      TEST_MODE: ctx.dev,
    },

    extendViteConf(viteConf) {
      viteConf.resolve = viteConf.resolve || {}
      viteConf.resolve.alias = {
        ...viteConf.resolve.alias,
        '@fullcalendar/core/vdom': '@fullcalendar/core/internal.js',
        boot: path.resolve(__dirname, './src/boot'),
        src: path.resolve(__dirname, './src'),
      }
    },

    // Test/Production settings based on ctx.dev for local testing and remote publishing
    publicPath: '/',
    // vueRouterBase,
    // vueDevtools,
    // vueOptionsAPI: false,

    // rebuildCache: true, // rebuilds Vite/linter/etc cache on startup

    target: {
      // Modern browser targets - automatically uses browserslist if .browserslistrc exists
      // Otherwise falls back to these sensible defaults
      browser: ['es2020', 'edge88', 'firefox78', 'chrome87', 'safari14'],
      node: 'node24',
    },
    // TypeScript support
    typescript: {
      extendTsConfig(tsConfig) {
        // Optional: extend the generated tsconfig
      },
      strict: true, // Full TypeScript strict mode enabled
      vueShim: true,
    },

    // analyze: true,
    // env: {},
    // rawDefine: {}
    // ignorePublicFolder: true,
    // minify: false,
    // polyfillModulePreload: true,
    // distDir

    vitePlugins: (() => {
      const plugins: any[] = [
        [
          '@intlify/unplugin-vue-i18n/vite',
          {
            // if you want to use Vue I18n Legacy API, you need to set `compositionOnly: false`
            // compositionOnly: false,

            // you need to set i18n resource including paths !
            include: path.resolve(__dirname, './src/i18n/**'),
            ssr: ctx.modeName === 'ssr',
          },
        ],
      ]

      // Image optimization plugin (only in production builds)
      if (ctx.prod) {
        plugins.push([
          'vite-plugin-imagemin',
          {
            // Skip GIF optimization (usually not needed for PWA)
            gifsicle: false,
            // Optimize JPEG files
            mozjpeg: {
              progressive: true,
              quality: 85,
            },
            // Optimize PNG files
            optipng: {
              optimizationLevel: 7,
            },
            // Optimize SVG files
            svgo: {
              plugins: [
                {
                  name: 'preset-default',
                  params: {
                    overrides: {
                      cleanupIds: {
                        minify: false, // Keep IDs readable for debugging
                      },
                      removeDimensions: false, // Keep width/height
                      removeViewBox: false, // Keep viewBox for responsive SVGs
                    },
                  },
                },
                {
                  active: true,
                  name: 'removeComments',
                },
                {
                  active: true,
                  name: 'removeTitle',
                },
                {
                  active: true,
                  name: 'removeDesc',
                },
              ],
            },
            // Optimize WebP files
            webp: {
              quality: 85,
            },
          },
        ])
      }

      return plugins
    })(),

    vueRouterMode: 'history', // available values: 'hash', 'history'
  },

  // Full list of options: https://v2.quasar.dev/quasar-cli/developing-capacitor-apps/configuring-capacitor
  capacitor: {
    hideSplashscreen: true,
  },

  // Full list of options: https://v2.quasar.dev/quasar-cli/developing-cordova-apps/configuring-cordova
  cordova: {
    // noIosLegacyBuildFlag: true, // uncomment only if you know what you are doing
  },

  // https://v2.quasar.dev/quasar-cli-vite/quasar-config-js#css
  css: [
    'app.scss',
    'override.scss', // Tenant-specific overrides loaded last
  ],

  // Full list of options: https://v2.quasar.dev/quasar-cli-vite/quasar-config-js#devServer
  devServer: {
    // https: true
    open: false, // don't open browser window automatically
    port: 9000,
    proxy: {},
  },

  // Full list of options: https://v2.quasar.dev/quasar-cli/developing-electron-apps/configuring-electron
  electron: {
    // extendElectronMainConf (esbuildConf)
    // extendElectronPreloadConf (esbuildConf)

    builder: {
      // https://www.electron.build/configuration/configuration

      appId: settings.appBasename + '-app',
    },

    bundler: 'packager', // 'packager' or 'builder'

    inspectPort: 5858,

    packager: {
      // https://github.com/electron-userland/electron-packager/blob/master/docs/api.md#options
      // OS X / Mac App Store
      // appBundleId: '',
      // appCategoryType: '',
      // osxSign: '',
      // protocol: 'myapp://path',
      // Windows only
      // win32metadata: { ... }
    },
  },

  // https://v2.quasar.dev/quasar-cli-vite/quasar-config-js#property-sourcefiles
  // sourceFiles: {
  //   rootComponent: 'src/App.vue',
  //   router: 'src/router/index',
  //   store: 'src/store/index',
  //   registerServiceWorker: 'src-pwa/register-service-worker',
  //   serviceWorker: 'src-pwa/custom-service-worker',
  //   pwaManifestFile: 'src-pwa/manifest.json',
  //   electronMain: 'src-electron/electron-main',
  //   electronPreload: 'src-electron/electron-preload'
  // },

  eslint: {
    errors: true,
    fix: true,
    // include = [],
    // exclude = [],
    // rawOptions = {},
    warnings: true,
  },

  // https://github.com/quasarframework/quasar/tree/dev/extras
  extras: [
    // 'ionicons-v4',
    // 'mdi-v5',
    // 'fontawesome-v6',
    // 'eva-icons',
    // 'themify',
    // 'line-awesome',
    // 'roboto-font-latin-ext', // this or either 'roboto-font', NEVER both!

    // 'roboto-font', // Disabled - using local fonts from config/fonts
    'material-icons', // optional, you are not bound to it
    'material-symbols-outlined', // Variable font with adjustable weight
  ],

  // https://v2.quasar.dev/quasar-cli-vite/quasar-config-js#framework
  framework: {
    config: {},

    // iconSet: 'material-icons', // Quasar icon set
    lang: 'de', // Quasar language pack

    // For special cases outside of where the auto-import strategy can have an impact
    // (like functional components as one of the examples),
    // you can manually specify Quasar components/directives to be available everywhere:
    //
    // components: [],
    // directives: [],

    // Quasar plugins
    plugins: ['Notify', 'Dark'],
  },

  // Add HTML template variables that can be used in index.html
  htmlVariables: {
    appBasename: settings.appBasename,
    backgroundColor: theme.backgroundColor,
    productDescription:
      settings.siteDescription || `${settings.siteName} Progressive Web App`,
    productName: settings.siteName,
    siteDescription: settings.siteDescription,
    siteName: settings.siteName,
    siteNickname: settings.siteNickname,
    themeColor: theme.primary,
  },

  // https://v2.quasar.dev/quasar-cli/developing-pwa/configuring-pwa
  pwa: {
    injectPwaMetaTags: true,
    manifestFilename: 'manifest.json',
    swFilename: 'sw.js',
    useCredentialsForManifestTag: false,
    workboxMode: 'InjectManifest', // or "GenerateSW"
    // useFilenameHashes: true,
    // extendGenerateSWOptions (cfg) {}
    // extendInjectManifestOptions (cfg) {},
    // extendManifestJson (json) {}
    // extendPWACustomSWConf (esbuildConf) {}
  },

  // https://v2.quasar.dev/quasar-cli/developing-ssr/configuring-ssr
  ssr: {
    // ssrPwaHtmlFilename: 'offline.html', // do NOT use index.html as name!
    // will mess up SSR

    // extendSSRWebserverConf (esbuildConf) {},
    // extendPackageJson (json) {},

    middlewares: [
      'render', // keep this as last one
    ],

    // manualStoreHydration: true,
    // manualPostHydrationTrigger: true,

    prodPort: 3000, // The default port that the production server should use
    // (gets superseded if process.env.PORT is specified at runtime)

    pwa: false,
  },
}))
