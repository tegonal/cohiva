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
  appBasename: z.string().min(1, 'appBasename cannot be empty'),
  buttonLinks: z.object({
    chat: ButtonLinkSchema,
    cloud: ButtonLinkSchema,
    handbuch: ButtonLinkSchema,
  }),
  domain: z
    .string()
    .min(1, 'domain cannot be empty')
    .regex(
      /^[a-z0-9]+([-.]{1}[a-z0-9]+)*\.[a-z]{2,}$/i,
      'domain must be a valid domain name'
    ),
  navigationLinks: z
    .array(NavigationLinkSchema)
    .min(1, 'At least one navigation link is required'),
  oauthClientId: z.string().min(1, 'oauthClientId cannot be empty'),
  passwordResetLink: z.string().url('passwordResetLink must be a valid URL'),
  prodHostname: z.string().min(1, 'prodHostname cannot be empty'),
  reservationLinks: z.object({
    links: z.array(ReservationLinkSchema),
    note: z.string(), // Can be empty
  }),
  siteDescription: z.string().min(1, 'siteDescription cannot be empty'),
  siteName: z.string().min(1, 'siteName cannot be empty'),
  siteNickname: z.string().min(1, 'siteNickname cannot be empty'),
  skipIconTrim: z.boolean().optional().default(false),
  testHostname: z.string().min(1, 'testHostname cannot be empty'),
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
export const ThemeSchema = z
  .object({
    accent: HexColorSchema,
    // Required app configuration colors (not exported to SCSS)
    backgroundColor: HexColorSchema,
    // Required dark mode colors
    dark: HexColorSchema,

    'dark-page': HexColorSchema,
    info: HexColorSchema,

    negative: HexColorSchema,
    // Required semantic colors
    positive: HexColorSchema,
    // Required Quasar brand colors
    primary: HexColorSchema,
    secondary: HexColorSchema,

    splashBackgroundColor: HexColorSchema,
    splashIconColor: HexColorSchema,
    themeColor: HexColorSchema,
    warning: HexColorSchema,
  })
  .catchall(z.string()) // Allow any additional string properties for custom SCSS variables

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
