import { renderHook, waitFor, act } from '@testing-library/react';
import { useQuery } from '@hooks/useQuery';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { useSettingsStore } from '@store/settings';

describe('useQuery', () => {
  beforeEach(() => {
    useSettingsStore.setState({ initialized: true, refreshIntervalMs: 0 });
  });

  it('marks data as stale when refresh interval passes', async () => {
    const fn = vi.fn().mockResolvedValue({ ok: true });
    const { result } = renderHook(() => useQuery(fn, { pollMs: 0, staleMs: 10 }));

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.data?.ok).toBe(true);

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 15));
    });
    expect(result.current.stale).toBe(true);
  });
});
