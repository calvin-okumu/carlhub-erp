// Local storage keys used throughout the application
export const STORAGE_KEYS = {
  ACCESS_TOKEN: "access",
  REFRESH_TOKEN: "refresh",
  USER_DATA: "user",
  TENANT: "tenant",
} as const;

export type StorageKey = (typeof STORAGE_KEYS)[keyof typeof STORAGE_KEYS];

