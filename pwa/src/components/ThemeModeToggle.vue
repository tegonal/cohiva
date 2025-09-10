<template>
  <q-btn-toggle
    v-model="themeMode"
    toggle-color="primary"
    :options="options"
    spread
    no-caps
    unelevated
    size="sm"
    class="theme-mode-toggle"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useThemeMode, type ThemeMode } from 'src/composables/use-theme-mode'

const { currentMode, setThemeMode } = useThemeMode()

const themeMode = computed({
  get: () => currentMode.value,
  set: (value: ThemeMode) => setThemeMode(value),
})

const options = [
  {
    label: 'System',
    value: 'system' as ThemeMode,
    icon: 'settings_brightness',
    slot: 'system',
  },
  {
    label: 'Hell',
    value: 'light' as ThemeMode,
    icon: 'light_mode',
    slot: 'light',
  },
  {
    label: 'Dunkel',
    value: 'dark' as ThemeMode,
    icon: 'dark_mode',
    slot: 'dark',
  },
]
</script>

<style scoped lang="scss">
.theme-mode-toggle {
  width: 100%;
  border-radius: $button-border-radius;
  
  :deep(.q-btn) {
    font-size: 0.75rem;
    padding: 4px 8px;
    
    .q-icon {
      font-size: 1.2rem;
    }
  }
}
</style>