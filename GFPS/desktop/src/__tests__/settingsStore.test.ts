import { describe, it, expect, beforeEach } from 'vitest';
import { useSettingsStore } from '@store/settings';

describe('settings store', () => {
  beforeEach(() => {
    localStorage.clear();
    useSettingsStore.setState({
      apiUrl: 'http://localhost:8000',
      refreshIntervalMs: 5000,
      evThreshold: 0.05,
      theme: 'dark',
      cacheTtlMs: 120000,
      forceOffline: false,
      autoOffline: true,
      storageStatus: 'idle',
      initialized: true
    });
  });

  it('persists encrypted settings', async () => {
    await useSettingsStore.getState().setApiUrl('http://api.test');
    const stored = localStorage.getItem('gfps_settings');
    expect(stored).toBeTruthy();
    expect(stored?.includes('api.test')).toBe(false);
  });

  it('hydrates saved settings', async () => {
    await useSettingsStore.getState().setEvThreshold(0.1);
    await useSettingsStore.getState().setCacheTtl(90000);
    await useSettingsStore.getState().setForceOffline(true);
    useSettingsStore.setState({ initialized: false, evThreshold: 0.05 });
    await useSettingsStore.getState().hydrate();
    expect(useSettingsStore.getState().evThreshold).toBeCloseTo(0.1);
    expect(useSettingsStore.getState().cacheTtlMs).toBe(90000);
    expect(useSettingsStore.getState().forceOffline).toBe(true);
    expect(useSettingsStore.getState().initialized).toBe(true);
  });
});
