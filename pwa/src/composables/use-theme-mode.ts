import { Dark } from 'quasar'
import { computed, ref, watch } from 'vue'

export type ThemeMode = 'dark' | 'light' | 'system'

const STORAGE_KEY = 'cohiva-theme-mode'

// Shared state across all component instances
const currentMode = ref<ThemeMode>('system')

// Initialize from localStorage on first load
const storedMode = localStorage.getItem(STORAGE_KEY) as null | ThemeMode
if (storedMode && ['dark', 'light', 'system'].includes(storedMode)) {
  currentMode.value = storedMode
}

// Apply the theme mode
function applyThemeMode(mode: ThemeMode) {
  switch (mode) {
    case 'dark':
      Dark.set(true)
      break
    case 'light':
      Dark.set(false)
      break
    case 'system':
      Dark.set('auto')
      break
  }
}

// Apply initial theme
applyThemeMode(currentMode.value)

// Watch for changes and persist to localStorage
watch(currentMode, (newMode) => {
  localStorage.setItem(STORAGE_KEY, newMode)
  applyThemeMode(newMode)
})

export function useThemeMode() {
  const isDark = computed(() => Dark.isActive)

  const setThemeMode = (mode: ThemeMode) => {
    currentMode.value = mode
  }

  const cycleThemeMode = () => {
    const modes: ThemeMode[] = ['system', 'light', 'dark']
    const currentIndex = modes.indexOf(currentMode.value)
    const nextIndex = (currentIndex + 1) % modes.length
    currentMode.value = modes[nextIndex]!
  }

  const themeModeIcon = computed(() => {
    switch (currentMode.value) {
      case 'dark':
        return 'dark_mode'
      case 'light':
        return 'light_mode'
      case 'system':
        return 'settings_brightness'
      default:
        return 'settings_brightness'
    }
  })

  const themeModeLabel = computed(() => {
    switch (currentMode.value) {
      case 'dark':
        return 'Dunkel'
      case 'light':
        return 'Hell'
      case 'system':
        return 'System'
      default:
        return 'System'
    }
  })

  return {
    currentMode: computed(() => currentMode.value),
    cycleThemeMode,
    isDark,
    setThemeMode,
    themeModeIcon,
    themeModeLabel,
  }
}
