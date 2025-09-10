import { boot } from 'quasar/wrappers'
import { useThemeMode } from 'src/composables/use-theme-mode'

/**
 * Dark Mode Boot File
 * 
 * Initializes the theme mode from localStorage preference.
 * The actual logic is handled by the use-theme-mode composable.
 */

export default boot(() => {
  // Initialize theme mode from localStorage
  // This ensures the composable is loaded and applies the saved preference
  const { currentMode } = useThemeMode()
  
  // Optional: Log the initial dark mode state for debugging
  if (process.env.DEV) {
    console.log('[Theme Mode] Initialized with mode:', currentMode.value)
  }
})