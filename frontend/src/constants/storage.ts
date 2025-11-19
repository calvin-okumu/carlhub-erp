// Local storage keys used throughout the application
// Centralizing these prevents typos and makes maintenance easier
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access',
  REFRESH_TOKEN: 'refresh',
  USER_DATA: 'user',
  TENANT: 'tenant'
} as const;

// Type for storage keys to ensure type safety
export type StorageKey = typeof STORAGE_KEYS[keyof typeof STORAGE_KEYS];