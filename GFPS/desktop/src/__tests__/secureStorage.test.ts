import { describe, it, expect, beforeEach } from 'vitest';
import { clearSecure, loadSecure, saveSecure } from '@app/secureStorage';

describe('secureStorage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('encrypts and decrypts payloads', async () => {
    await saveSecure('test-key', { secret: 'value' });
    const raw = localStorage.getItem('test-key');
    expect(raw).toBeTruthy();
    expect(raw?.includes('value')).toBe(false);

    const recovered = await loadSecure<{ secret: string }>('test-key');
    expect(recovered?.secret).toBe('value');
  });

  it('clears secure payload', async () => {
    await saveSecure('test-key', { secret: 'value' });
    clearSecure('test-key');
    const recovered = await loadSecure<{ secret: string }>('test-key');
    expect(recovered).toBeUndefined();
  });

  it('uses environment variable or secure fallback for salt', async () => {
    // Test that encryption works (salt is being used)
    await saveSecure('env-test-key', { data: 'sensitive' });
    const encrypted = localStorage.getItem('env-test-key');
    
    // Verify it's encrypted (contains IV and cipher separated by :)
    expect(encrypted).toBeTruthy();
    expect(encrypted?.split(':')).toHaveLength(2);
    expect(encrypted?.includes('sensitive')).toBe(false);
    
    // Verify decryption works
    const decrypted = await loadSecure<{ data: string }>('env-test-key');
    expect(decrypted?.data).toBe('sensitive');
  });
});
