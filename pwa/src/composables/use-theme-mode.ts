import { ref, watch, computed } from 'vue'
import { Dark } from 'quasar'

export type ThemeMode = 'system' | 'light' | 'dark'

const STORAGE_KEY = 'cohiva-theme-mode'

// Shared state across all component instances
const currentMode = ref<ThemeMode>('system')

// Initialize from localStorage on first load
const storedMode = localStorage.getItem(STORAGE_KEY) as ThemeMode | null
if (storedMode && ['system', 'light', 'dark'].includes(storedMode)) {
  currentMode.value = storedMode
}

// Apply the theme mode
function applyThemeMode(mode: ThemeMode) {
  switch (mode) {
    case 'system':
      Dark.set('auto')
      break
    case 'light':
      Dark.set(false)
      break
    case 'dark':
      Dark.set(true)
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
      case 'system':
        return 'settings_brightness'
      case 'light':
        return 'light_mode'
      case 'dark':
        return 'dark_mode'
      default:
        return 'settings_brightness'
    }
  })
  
  const themeModeLabel = computed(() => {
    switch (currentMode.value) {
      case 'system':
        return 'System'
      case 'light':
        return 'Hell'
      case 'dark':
        return 'Dunkel'
      default:
        return 'System'
    }
  })
  
  return {
    currentMode: computed(() => currentMode.value),
    isDark,
    setThemeMode,
    cycleThemeMode,
    themeModeIcon,
    themeModeLabel,
  }
}