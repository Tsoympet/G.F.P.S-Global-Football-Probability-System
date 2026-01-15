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
});
