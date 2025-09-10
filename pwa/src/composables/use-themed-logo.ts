import { Dark } from 'quasar'
import { computed } from 'vue'

/**
 * Composable for getting theme-aware logo and icon paths
 * Automatically switches between light and dark versions based on current theme
 */
export function useThemedLogo() {
  // Reactive computed properties that update when dark mode changes
  const logoPath = computed(() => {
    return Dark.isActive 
      ? '/src/assets/logo-dark.svg' 
      : '/src/assets/logo.svg'
  })

  const iconPath = computed(() => {
    return Dark.isActive 
      ? '/src/assets/icon-dark.svg' 
      : '/src/assets/icon.svg'
  })

  // For CSS background images, we can use CSS classes instead
  const logoClass = computed(() => {
    return Dark.isActive ? 'logo-dark' : 'logo-light'
  })

  return {
    logoPath,
    iconPath,
    logoClass,
  }
}