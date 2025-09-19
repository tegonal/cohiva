/* eslint-disable */

import type { Theme } from './schemas'

// Light theme colors (default)
const theme: Theme = {
  // Brand Colors
  primary: '#2563EB',
  secondary: '#10B981',
  accent: '#8B5CF6',

  // Dark Mode
  dark: '#1F2937',
  'dark-page': '#111827',

  // Semantic Colors
  positive: '#22C55E',
  negative: '#EF4444',
  info: '#06B6D4',
  warning: '#F59E0B',

  // App Colors (not exported to SCSS)
  backgroundColor: '#FFFFFF',
  themeColor: '#2563EB',
  splashBackgroundColor: '#2563EB',
  splashIconColor: '#FFFFFF',

  // Custom SCSS Variables (will be auto-exported)
  'link-color': '#2563EB',
  'link-hover-color': '#1d4ed8',
  'link-visited-color': '#2563EB',
  'link-active-color': '#1e40af',

  'typography-font-family':
    "'Roboto', 'Helvetica Neue', Helvetica, Arial, sans-serif",

  'generic-border-radius': '4px',
  'button-border-radius': '4px',

  'shadow-1': '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
  'shadow-2': '0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)',
  'shadow-3': '0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)',
  'shadow-4': '0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22)',
  'shadow-5': '0 19px 38px rgba(0,0,0,0.30), 0 15px 12px rgba(0,0,0,0.22)',

  // Custom spacing - using simple values that won't conflict with Quasar
  'custom-space-xs': '4px',
  'custom-space-sm': '8px',
  'custom-space-md': '16px',
  'custom-space-lg': '24px',
  'custom-space-xl': '32px',

  // Header/Toolbar colors
  'header-bg': '#f5f5f9', // Light gray header background
  'header-text': '#1F2937',
  'header-shadow': '0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)', // Uses shadow-2 value
  'toolbar-bg': 'transparent',
  'toolbar-text': 'inherit',

  // Dark theme overrides (prefixed with dark-)
  'dark-primary': '#2563EB', // Lighter blue for dark mode
  'dark-secondary': '#34D399', // Lighter green for dark mode
  'dark-accent': '#A78BFA', // Lighter purple for dark mode
  'dark-positive': '#4ADE80',
  'dark-negative': '#F87171',
  'dark-info': '#22D3EE',
  'dark-warning': '#FBBF24',

  'dark-link-color': '#60A5FA',
  'dark-link-hover-color': '#93BBFC',
  'dark-link-visited-color': '#60A5FA',
  'dark-link-active-color': '#3B82F6',

  'dark-shadow-1': '0 1px 3px rgba(0,0,0,0.5), 0 1px 2px rgba(0,0,0,0.6)',
  'dark-shadow-2': '0 3px 6px rgba(0,0,0,0.6), 0 3px 6px rgba(0,0,0,0.7)',
  'dark-shadow-3': '0 10px 20px rgba(0,0,0,0.7), 0 6px 6px rgba(0,0,0,0.8)',
  'dark-shadow-4': '0 14px 28px rgba(0,0,0,0.8), 0 10px 10px rgba(0,0,0,0.85)',
  'dark-shadow-5': '0 19px 38px rgba(0,0,0,0.9), 0 15px 12px rgba(0,0,0,0.85)',

  // Dark theme header/toolbar colors
  'dark-header-bg': '#1F2937', // Dark gray for header
  'dark-header-text': '#F3F4F6',
  'dark-header-shadow': '0 3px 6px rgba(0,0,0,0.6), 0 3px 6px rgba(0,0,0,0.7)', // Uses dark-shadow-2 value
  'dark-toolbar-bg': 'transparent',
  'dark-toolbar-text': 'inherit',
}

export default theme
