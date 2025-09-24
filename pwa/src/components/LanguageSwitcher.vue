<template>
  <q-btn-dropdown
    flat
    dense
    icon="language"
    size="sm"
    class="language-switcher"
  >
    <q-list>
      <q-item
        v-for="lang in languages"
        :key="lang.value"
        clickable
        v-close-popup
        @click="changeLanguage(lang.value)"
      >
        <q-item-section>
          <q-item-label>{{ lang.label }}</q-item-label>
        </q-item-section>
        <q-item-section side v-if="currentLocale === lang.value">
          <q-icon name="check" color="primary" />
        </q-item-section>
      </q-item>
    </q-list>
  </q-btn-dropdown>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

const languages = [
  { label: 'Deutsch', value: 'de-CH' },
  { label: 'English', value: 'en-US' },
  { label: 'Français', value: 'fr-FR' },
]

const currentLocale = computed(() => locale.value)

function changeLanguage(newLocale: string) {
  locale.value = newLocale
  // Save preference to localStorage
  localStorage.setItem('user-locale', newLocale)
}
</script>

<style lang="scss" scoped>
.language-switcher {
  :deep(.q-btn-dropdown__arrow) {
    margin-left: 2px;
  }
}
</style>
