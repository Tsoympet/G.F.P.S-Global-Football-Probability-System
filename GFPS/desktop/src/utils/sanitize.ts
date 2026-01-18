/**
 * Security utilities for preventing prototype pollution attacks
 */

/**
 * Sanitizes a key by prepending it with '$' to prevent access to built-in
 * object properties like __proto__, constructor, etc.
 *
 * This prevents prototype pollution attacks where user-controlled data
 * is used as object property names.
 *
 * @param key - The key to sanitize
 * @returns The sanitized key with '$' prefix
 */
export const sanitizeKey = (key: string): string => `$${key}`;

/**
 * Sanitizes all keys in a Record object to prevent prototype pollution.
 *
 * @param record - The record object to sanitize
 * @returns A new record with all keys prefixed with '$'
 */
export const sanitizeRecord = <T,>(record: Record<string, T>): Record<string, T> => {
  const sanitized: Record<string, T> = {};
  for (const key in record) {
    if (Object.prototype.hasOwnProperty.call(record, key)) {
      sanitized[sanitizeKey(key)] = record[key];
    }
  }
  return sanitized;
};
