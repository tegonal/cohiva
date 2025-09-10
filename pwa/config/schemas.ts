import { z } from 'zod'

/**
 * Zod schemas for configuration validation
 * These schemas ensure configuration files are valid before building
 */

// Schema for button links
const ButtonLinkSchema = z.object({
  link: z.string().url('Button link must be a valid URL'),
})

// Schema for navigation links
const NavigationLinkSchema = z.object({
  caption: z.string().min(1, 'Navigation caption cannot be empty'),
  icon: z.string().min(1, 'Navigation icon cannot be empty'),
  link: z.string().url('Navigation link must be a valid URL'),
  title: z.string().min(1, 'Navigation title cannot be empty'),
})

// Schema for reservation links
const ReservationLinkSchema = z.object({
  caption: z.string().min(1, 'Reservation caption cannot be empty'),
  link: z.string().url('Reservation link must be a valid URL'),
  title: z.string().min(1, 'Reservation title cannot be empty'),
})

// Main settings schema
export const SettingsSchema = z.object({
  APP_BASENAME: z.string().min(1, 'APP_BASENAME cannot be empty'),
  BUTTON_LINKS: z.object({
    CHAT: ButtonLinkSchema,
    CLOUD: ButtonLinkSchema,
    HANDBUCH: ButtonLinkSchema,
  }),
  DOMAIN: z
    .string()
    .min(1, 'DOMAIN cannot be empty')
    .regex(
      /^[a-z0-9]+([-.]{1}[a-z0-9]+)*\.[a-z]{2,}$/i,
      'DOMAIN must be a valid domain name'
    ),
  NAVIGATION_LINKS: z
    .array(NavigationLinkSchema)
    .min(1, 'At least one navigation link is required'),
  OAUTH_CLIENT_ID: z.string().min(1, 'OAUTH_CLIENT_ID cannot be empty'),
  PASSWORD_RESET_LINK: z
    .string()
    .url('PASSWORD_RESET_LINK must be a valid URL'),
  PROD_HOSTNAME: z.string().min(1, 'PROD_HOSTNAME cannot be empty'),
  RESERVATION_LINKS: z.object({
    LINKS: z.array(ReservationLinkSchema),
    NOTE: z.string(), // Can be empty
  }),
  SITE_DESCRIPTION: z.string().min(1, 'SITE_DESCRIPTION cannot be empty'),
  SITE_NAME: z.string().min(1, 'SITE_NAME cannot be empty'),
  SITE_NICKNAME: z.string().min(1, 'SITE_NICKNAME cannot be empty'),
  TEST_HOSTNAME: z.string().min(1, 'TEST_HOSTNAME cannot be empty'),
})

// Color validation regex (hex color)
const HexColorSchema = z
  .string()
  .regex(/^#[0-9A-Fa-f]{6}$/, 'Must be a valid hex color (e.g., #1976D2)')

// CSS value schemas for different types
const CSSLengthSchema = z
  .string()
  .regex(/^\d+(\.\d+)?(px|em|rem|%|vh|vw)$/, 'Must be a valid CSS length value')

const CSSShadowSchema = z
  .string()
  .regex(/^[^;]+$/, 'Must be a valid CSS shadow value')

const CSSTransitionSchema = z
  .string()
  .regex(/^[^;]+$/, 'Must be a valid CSS transition value')

// Theme configuration schema with strict required fields and flexible additional properties
export const ThemeSchema = z.object({
  // Required Quasar brand colors
  primary: HexColorSchema,
  secondary: HexColorSchema,
  accent: HexColorSchema,

  // Required dark mode colors
  dark: HexColorSchema,
  'dark-page': HexColorSchema,

  // Required semantic colors
  positive: HexColorSchema,
  negative: HexColorSchema,
  info: HexColorSchema,
  warning: HexColorSchema,

  // Required app configuration colors (not exported to SCSS)
  backgroundColor: HexColorSchema,
  themeColor: HexColorSchema,
  splashBackgroundColor: HexColorSchema,
  splashIconColor: HexColorSchema,
}).catchall(z.string()) // Allow any additional string properties for custom SCSS variables

// Type exports for TypeScript
export type ButtonLink = z.infer<typeof ButtonLinkSchema>
export type NavigationLink = z.infer<typeof NavigationLinkSchema>
export type ReservationLink = z.infer<typeof ReservationLinkSchema>
export type Settings = z.infer<typeof SettingsSchema>
export type Theme = z.infer<typeof ThemeSchema>

// Validation functions with better error messages
export function validateSettings(settings: unknown): Settings {
  try {
    return SettingsSchema.parse(settings)
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errorMessages = error.issues
        .map((err) => `  - ${err.path.join('.')}: ${err.message}`)
        .join('\n')
      throw new Error(`Settings validation failed:\n${errorMessages}`)
    }
    throw error
  }
}

export function validateTheme(theme: unknown): Theme {
  try {
    return ThemeSchema.parse(theme)
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errorMessages = error.issues
        .map((err) => `  - ${err.path.join('.')}: ${err.message}`)
        .join('\n')
      throw new Error(`Theme validation failed:\n${errorMessages}`)
    }
    throw error
  }
}
