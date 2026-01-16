import { clearSecure, loadSecure, saveSecure } from '@app/secureStorage';

const CACHE_PREFIX = 'gfps_cache';
// Keep cached payloads alive for up to double the TTL so offline mode has a safe fallback window.
const EXPIRY_MULTIPLIER = 2;

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttlMs: number;
}

export const loadCached = async <T>(key: string, ttlMs: number) => {
  const entry = await loadSecure<CacheEntry<T>>(`${CACHE_PREFIX}:${key}`);
  if (!entry) return undefined;
  const expiresIn = entry.ttlMs ?? ttlMs;
  const age = Date.now() - entry.timestamp;
  if (expiresIn && age > expiresIn * EXPIRY_MULTIPLIER) {
    clearSecure(`${CACHE_PREFIX}:${key}`);
    return undefined;
  }
  return { data: entry.data, stale: expiresIn ? age > expiresIn : false, timestamp: entry.timestamp };
};

export const saveCached = async <T>(key: string, data: T, ttlMs: number) => {
  const entry: CacheEntry<T> = { data, timestamp: Date.now(), ttlMs };
  await saveSecure(`${CACHE_PREFIX}:${key}`, entry);
  return entry.timestamp;
};

export const clearCached = (key: string) => clearSecure(`${CACHE_PREFIX}:${key}`);
