/* eslint-env node */

/*
 * This file runs in a Node context (it's NOT transpiled by Babel), so use only
 * the ES6 features that are supported by your Node version. https://node.green/
 */

// Configuration for your app
// https://v2.quasar.dev/quasar-cli-vite/quasar-config-js

import { settings } from './config/settings.js'
import theme from './config/theme.js'
import { defineConfig } from '#q-app/wrappers'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

export default defineConfig(function (ctx) {
  return {
    // Add HTML template variables that can be used in index.html
    htmlVariables: {
      productName: settings.SITE_NAME,
      productDescription:
        settings.SITE_DESCRIPTION ||
        `${settings.SITE_NAME} Progressive Web App`,
      siteName: settings.SITE_NAME,
      siteNickname: settings.SITE_NICKNAME,
      siteDescription: settings.SITE_DESCRIPTION,
      appBasename: settings.APP_BASENAME,
      themeColor: theme.primary,
      backgroundColor: theme.backgroundColor,
    },

    eslint: {
      // fix: true,
      // include = [],
      // exclude = [],
      // rawOptions = {},
      warnings: true,
      errors: true,
    },

    // https://v2.quasar.dev/quasar-cli/prefetch-feature
    // preFetch: true,

    // app boot file (/src/boot)
    // --> boot files are part of "main.js"
    // https://v2.quasar.dev/quasar-cli/boot-files
    boot: ['i18n', 'axios'],

    // https://v2.quasar.dev/quasar-cli-vite/quasar-config-js#css
    css: [
      'app.scss',
      'override.scss' // Tenant-specific overrides loaded last
    ],

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
    ],

    // Full list of options: https://v2.quasar.dev/quasar-cli-vite/quasar-config-js#build
    build: {
      target: {
        browser: ['es2019', 'edge88', 'firefox78', 'chrome87', 'safari13.1'],
        node: 'node16',
      },

      vueRouterMode: 'hash', // available values: 'hash', 'history'
      // vueRouterBase,
      // vueDevtools,
      // vueOptionsAPI: false,

      // rebuildCache: true, // rebuilds Vite/linter/etc cache on startup

      // Test/Production settings based on ctx.dev for local testing and remote publishing
      publicPath: '/',
      env: {
        TEST_MODE: ctx.dev ? true : false,
        API: ctx.dev
          ? '/api-proxy/' // Use proxy in development to avoid CORS
          : 'https://' + settings.PROD_HOSTNAME + '.' + settings.DOMAIN + '/',
        API_DIRECT: ctx.dev
          ? 'https://' + settings.TEST_HOSTNAME + '.' + settings.DOMAIN + '/'
          : 'https://' + settings.PROD_HOSTNAME + '.' + settings.DOMAIN + '/',
      },

      // analyze: true,
      // env: {},
      // rawDefine: {}
      // ignorePublicFolder: true,
      // minify: false,
      // polyfillModulePreload: true,
      // distDir

      // extendViteConf (viteConf) {},
      // viteVuePluginOptions: {},

      vitePlugins: [
        [
          () =>
            import('@intlify/unplugin-vue-i18n/vite').then((m) => m.default),
          {
            // if you want to use Vue I18n Legacy API, you need to set `compositionOnly: false`
            // compositionOnly: false,

            // you need to set i18n resource including paths !
            include: path.resolve(__dirname, './src/i18n/**'),
            ssr: ctx.modeName === 'ssr',
          },
        ],
        // Image optimization plugin (only in production builds)
        ctx.prod && [
          () =>
            import('vite-plugin-imagemin').then((m) => m.default),
          {
            // Optimize SVG files
            svgo: {
              plugins: [
                {
                  name: 'preset-default',
                  params: {
                    overrides: {
                      removeViewBox: false, // Keep viewBox for responsive SVGs
                      removeDimensions: false, // Keep width/height
                      cleanupIds: {
                        minify: false // Keep IDs readable for debugging
                      }
                    }
                  }
                },
                {
                  name: 'removeComments',
                  active: true
                },
                {
                  name: 'removeTitle',
                  active: true
                },
                {
                  name: 'removeDesc',
                  active: true
                }
              ]
            },
            // Optimize PNG files
            optipng: {
              optimizationLevel: 7
            },
            // Optimize JPEG files
            mozjpeg: {
              quality: 85,
              progressive: true
            },
            // Optimize WebP files
            webp: {
              quality: 85
            },
            // Skip GIF optimization (usually not needed for PWA)
            gifsicle: false
          }
        ]
      ].filter(Boolean), // Filter out false values when not in production

      extendViteConf(viteConf) {
        viteConf.resolve = viteConf.resolve || {}
        viteConf.resolve.alias = {
          ...viteConf.resolve.alias,
          '@fullcalendar/core/vdom': '@fullcalendar/core/internal.js',
          boot: path.resolve(__dirname, './src/boot'),
          src: path.resolve(__dirname, './src'),
        }
      },
    },

    // Full list of options: https://v2.quasar.dev/quasar-cli-vite/quasar-config-js#devServer
    devServer: {
      // https: true
      open: false, // don't open browser window automatically
      port: 9000,
      proxy: {
        // Proxy all API calls to avoid CORS in development
        '/api-proxy': {
          target: `https://${settings.PROD_HOSTNAME}.${settings.DOMAIN}`,
          changeOrigin: true,
          secure: false, // Set to false if you have certificate issues
          rewrite: (path) => path.replace(/^\/api-proxy/, ''),
          configure: (proxy, options) => {
            proxy.on('error', (err, req, res) => {
              console.log('proxy error', err)
            })
            proxy.on('proxyReq', (proxyReq, req, res) => {
              console.log(
                'Proxying:',
                req.method,
                req.url,
                '->',
                options.target + req.url
              )
            })
          },
        },
      },
    },

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
      plugins: ['Notify'],
    },

    // animations: 'all', // --- includes all animations
    // https://v2.quasar.dev/options/animations
    animations: [],

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

    // https://v2.quasar.dev/quasar-cli/developing-ssr/configuring-ssr
    ssr: {
      // ssrPwaHtmlFilename: 'offline.html', // do NOT use index.html as name!
      // will mess up SSR

      // extendSSRWebserverConf (esbuildConf) {},
      // extendPackageJson (json) {},

      pwa: false,

      // manualStoreHydration: true,
      // manualPostHydrationTrigger: true,

      prodPort: 3000, // The default port that the production server should use
      // (gets superseded if process.env.PORT is specified at runtime)

      middlewares: [
        'render', // keep this as last one
      ],
    },

    // https://v2.quasar.dev/quasar-cli/developing-pwa/configuring-pwa
    pwa: {
      workboxMode: 'InjectManifest', // or "GenerateSW"
      injectPwaMetaTags: true,
      swFilename: 'sw.js',
      manifestFilename: 'manifest.json',
      useCredentialsForManifestTag: false,
      // useFilenameHashes: true,
      // extendGenerateSWOptions (cfg) {}
      // extendInjectManifestOptions (cfg) {},
      // extendManifestJson (json) {}
      // extendPWACustomSWConf (esbuildConf) {}
    },

    // Full list of options: https://v2.quasar.dev/quasar-cli/developing-cordova-apps/configuring-cordova
    cordova: {
      // noIosLegacyBuildFlag: true, // uncomment only if you know what you are doing
    },

    // Full list of options: https://v2.quasar.dev/quasar-cli/developing-capacitor-apps/configuring-capacitor
    capacitor: {
      hideSplashscreen: true,
    },

    // Full list of options: https://v2.quasar.dev/quasar-cli/developing-electron-apps/configuring-electron
    electron: {
      // extendElectronMainConf (esbuildConf)
      // extendElectronPreloadConf (esbuildConf)

      inspectPort: 5858,

      bundler: 'packager', // 'packager' or 'builder'

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

      builder: {
        // https://www.electron.build/configuration/configuration

        appId: settings.APP_BASENAME + '-app',
      },
    },

    // Full list of options: https://v2.quasar.dev/quasar-cli-vite/developing-browser-extensions/configuring-bex
    bex: {
      contentScripts: ['my-content-script'],

      // extendBexScriptsConf (esbuildConf) {}
      // extendBexManifestJson (json) {}
    },
  }
})
