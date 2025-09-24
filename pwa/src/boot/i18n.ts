import { defineBoot } from '#q-app/wrappers'
import browserLang from 'browser-lang'
import { createI18n } from 'vue-i18n'

import messages from 'src/i18n'

// Detect browser language and map to supported locale
function getBrowserLocale(): string {
  // Only run on client side
  if (typeof window === 'undefined' || typeof navigator === 'undefined') {
    return 'en-US'
  }

  // Check localStorage for saved preference
  const savedLocale = localStorage.getItem('user-locale')
  if (savedLocale && savedLocale in messages) {
    return savedLocale
  }

  // Use browser-lang library to detect browser language
  // It handles various browser quirks and fallbacks automatically
  const detectedLang = browserLang({
    fallback: 'en',
    languages: ['de', 'en', 'fr'], // Our supported language codes
  })

  // Map detected language to our canonical locales
  const localeMap: Record<string, string> = {
    de: 'de-CH', // All German variants use Swiss German
    en: 'en-US', // All English variants use US English
    fr: 'fr-FR', // All French variants use French
  }

  return localeMap[detectedLang] || 'en-US'
}

export default defineBoot(({ app }) => {
  const detectedLocale = getBrowserLocale()

  const i18n = createI18n({
    fallbackLocale: 'en-US', // Fallback to English if translation missing
    fallbackWarn: false,
    globalInjection: true,
    locale: detectedLocale,
    messages,
    // Suppress warnings for missing translations during development
    missingWarn: false,
  })

  app.use(i18n)
})
