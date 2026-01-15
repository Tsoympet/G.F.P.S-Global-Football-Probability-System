export const isOffline = (forceOffline: boolean, autoOffline: boolean) =>
  forceOffline || (autoOffline && typeof navigator !== 'undefined' && navigator && !navigator.onLine);
