const encoder = new TextEncoder();
const decoder = new TextDecoder();

// Use environment variable for secret salt, with a secure fallback
// In production, VITE_SECRET_SALT should be set at build time
const SECRET_SALT =
  import.meta.env.VITE_SECRET_SALT ||
  (() => {
    // Fallback: generate a deterministic but unique value per browser/device
    // Must be deterministic to ensure the same key is derived across page loads
    // for successful decryption. This is less secure than a build-time secret
    // but better than a hardcoded value shared across all installations.
    const hasNavigator = typeof navigator !== 'undefined';
    const userAgent = hasNavigator ? navigator.userAgent : '';
    const platform = hasNavigator ? (navigator.platform || 'unknown') : 'unknown';
    return `gfps-${btoa(userAgent + platform).substring(0, 32)}`;
  })();

const getCrypto = () => {
  const cryptoFromGlobal = (globalThis as { crypto?: Crypto }).crypto;
  if (cryptoFromGlobal?.subtle && cryptoFromGlobal.getRandomValues) {
    return cryptoFromGlobal;
  }

  // Vitest/jsdom fallback
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { webcrypto } = require('crypto');
  return webcrypto as Crypto;
};

const toBase64 = (buffer: ArrayBuffer) => {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  bytes.forEach((b) => (binary += String.fromCharCode(b)));
  return btoa(binary);
};

const fromBase64 = (value: string) => {
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
};

const deriveKey = async () => {
  const crypto = getCrypto();
  const material = await crypto.subtle.importKey(
    'raw',
    encoder.encode(`${SECRET_SALT}-${navigator.userAgent}-${navigator.platform || 'web'}`),
    'PBKDF2',
    false,
    ['deriveKey']
  );

  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: encoder.encode('gfps-desktop-salt'),
      iterations: 120_000,
      hash: 'SHA-256'
    },
    material,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  );
};

export const encryptPayload = async (plaintext: string) => {
  const crypto = getCrypto();
  const key = await deriveKey();
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, encoder.encode(plaintext));
  return `${toBase64(iv)}:${toBase64(encrypted)}`;
};

export const decryptPayload = async (payload: string) => {
  const crypto = getCrypto();
  const key = await deriveKey();
  const [ivEncoded, cipherEncoded] = payload.split(':');
  if (!ivEncoded || !cipherEncoded) throw new Error('Invalid payload');
  const decrypted = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv: fromBase64(ivEncoded) },
    key,
    fromBase64(cipherEncoded)
  );
  return decoder.decode(decrypted);
};

export const saveSecure = async <T>(key: string, value: T) => {
  const payload = await encryptPayload(JSON.stringify(value));
  localStorage.setItem(key, payload);
  return new Date().toISOString();
};

export const loadSecure = async <T>(key: string): Promise<T | undefined> => {
  const payload = localStorage.getItem(key);
  if (!payload) return undefined;
  try {
    const decrypted = await decryptPayload(payload);
    return JSON.parse(decrypted) as T;
  } catch (err) {
    console.warn('Failed to decrypt local data', err);
    return undefined;
  }
};

export const clearSecure = (key: string) => {
  localStorage.removeItem(key);
};
