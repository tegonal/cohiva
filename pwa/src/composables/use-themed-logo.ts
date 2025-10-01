import { Dark } from 'quasar'
import { computed } from 'vue'

import logoDark from '../assets/logo-dark.svg'
import logoLight from '../assets/logo.svg'

/**
 * Composable for getting theme-aware logo and icon paths
 * Automatically switches between light and dark versions based on current theme
 */
export function useThemedLogo() {
  // Reactive computed properties that update when dark mode changes
  const logoPath = computed(() => {
    return Dark.isActive ? logoDark : logoLight
  })

  // For CSS background images, we can use CSS classes instead
  const logoClass = computed(() => {
    return Dark.isActive ? 'logo-dark' : 'logo-light'
  })

  return {
    logoClass,
    logoPath,
  }
}
