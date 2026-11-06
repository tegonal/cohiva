import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import pluginPerfectionist from 'eslint-plugin-perfectionist'
import typescriptEslint from '@typescript-eslint/eslint-plugin'
import typescriptParser from '@typescript-eslint/parser'
import globals from 'globals'
import vueParser from 'vue-eslint-parser'

export default [
  js.configs.recommended,
  ...pluginVue.configs['flat/essential'],
  {
    plugins: {
      perfectionist: pluginPerfectionist,
    },
    rules: {
      ...pluginPerfectionist.configs['recommended-natural'].rules,
      // Imports: consistent ordering
      'perfectionist/sort-imports': [
        'error',
        {
          type: 'natural',
          order: 'asc',
          groups: [
            'type',
            ['builtin', 'external'],
            'internal',
            ['parent', 'sibling', 'index'],
            'unknown',
          ],
          internalPattern: ['^@/', '^app/', '^\\.\\./'],
        },
      ],
      // Enums: consistent ordering
      'perfectionist/sort-enums': [
        'error',
        {
          type: 'alphabetical',
          order: 'asc',
        },
      ],
      // Object types: keep properties consistent
      'perfectionist/sort-object-types': [
        'error',
        {
          type: 'alphabetical',
          order: 'asc',
        },
      ],
      // Objects: preserve developer-defined logical order
      'perfectionist/sort-objects': [
        'error',
        {
          type: 'unsorted',
          newlinesBetween: 'ignore',
        },
      ],
    },
  },
  {
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.node,
        ga: 'readonly',
        cordova: 'readonly',
        __statics: 'readonly',
        __QUASAR_SSR__: 'readonly',
        __QUASAR_SSR_SERVER__: 'readonly',
        __QUASAR_SSR_CLIENT__: 'readonly',
        __QUASAR_SSR_PWA__: 'readonly',
        Capacitor: 'readonly',
        chrome: 'readonly',
      },
    },
    rules: {
      'no-unused-vars': 'off',
      'no-useless-assignment': 'off',
      '@typescript-eslint/no-unused-vars': 'warn',
      'vue/multi-word-component-names': 'off',
      'vue/no-reserved-component-names': 'off',
      'vue/component-name-in-template-casing': ['error', 'PascalCase'],
      'vue/valid-v-slot': [
        'error',
        {
          allowModifiers: true,
        },
      ],
    },
  },
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: typescriptParser,
    },
    plugins: {
      '@typescript-eslint': typescriptEslint,
    },
    rules: {
      ...typescriptEslint.configs.recommended.rules,
      'no-undef': 'off', // TypeScript handles this
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-unused-vars': 'warn',
    },
  },
  {
    files: ['**/*.vue'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: typescriptParser,
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
    plugins: {
      '@typescript-eslint': typescriptEslint,
    },
    rules: {
      ...typescriptEslint.configs.recommended.rules,
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-unused-vars': 'warn',
    },
  },
  {
    files: ['src-pwa/sw/**/*.ts'],
    languageOptions: {
      parser: typescriptParser,
      globals: {
        ...globals.serviceworker,
      },
    },
    plugins: {
      '@typescript-eslint': typescriptEslint,
    },
    rules: {
      ...typescriptEslint.configs.recommended.rules,
      'no-undef': 'off',
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-unused-vars': 'warn',
    },
  },
  {
    ignores: [
      '.DS_Store',
      '.thumbs.db',
      'node_modules',
      '.quasar',
      '/dist',
      '/src-capacitor',
      '/src-cordova',
      '/.idea',
      '*.suo',
      '*.ntvs*',
      '*.njsproj',
      '*.sln',
      '*.sw?',
      'npm-debug.log*',
      'yarn-debug.log*',
      'yarn-error.log*',
      'pnpm-debug.log*',
      'lerna-debug.log*',
      '**/*.js',
      '**/*.mjs',
      '**/*.cjs',
    ],
  },
]
