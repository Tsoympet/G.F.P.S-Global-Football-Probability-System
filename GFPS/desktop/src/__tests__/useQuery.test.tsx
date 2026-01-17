import { renderHook, waitFor, act } from '@testing-library/react';
import { useQuery } from '@hooks/useQuery';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { useSettingsStore } from '@store/settings';
import { saveCached } from '@app/cache';

describe('useQuery', () => {
  beforeEach(() => {
    useSettingsStore.setState({
      initialized: true,
      refreshIntervalMs: 0,
      cacheTtlMs: 1000,
      autoOffline: true,
      forceOffline: false
    });
  });

  it('marks data as stale when refresh interval passes', async () => {
    const fn = vi.fn().mockResolvedValue({ ok: true });
    const { result } = renderHook(() => useQuery(fn, { pollMs: 0, staleMs: 10 }));

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect((result.current.data as { ok: boolean })?.ok).toBe(true);

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 15));
    });
    expect(result.current.stale).toBe(true);
  });

  it('uses cached data when offline', async () => {
    await saveCached('cached-test', { ok: 'cached' }, 5000);
    useSettingsStore.setState({ forceOffline: true });
    const fn = vi.fn().mockResolvedValue({ ok: 'network' });
    const { result } = renderHook(() => useQuery(fn, { pollMs: 0, cacheKey: 'cached-test' }));

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect((result.current.data as { ok: string })?.ok).toBe('cached');
    await waitFor(() => expect(result.current.stale).toBe(true));
  });
});
