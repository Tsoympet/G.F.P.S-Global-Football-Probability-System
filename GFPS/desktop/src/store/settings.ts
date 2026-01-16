import { loadSecure, saveSecure } from '@app/secureStorage';
import { create } from 'zustand';

type Theme = 'dark' | 'contrast';

type StorageStatus = 'idle' | 'loading' | 'persisted' | 'error';

const SETTINGS_KEY = 'gfps_settings';

type PersistedSettings = {
  apiUrl: string;
  refreshIntervalMs: number;
  evThreshold: number;
  theme: Theme;
  cacheTtlMs: number;
  forceOffline: boolean;
  autoOffline: boolean;
  lastSaved?: string;
};

export interface SettingsState extends PersistedSettings {
  storageStatus: StorageStatus;
  initialized: boolean;
  storageMessage?: string;
  setApiUrl: (apiUrl: string) => Promise<void>;
  setRefreshInterval: (ms: number) => Promise<void>;
  setEvThreshold: (ev: number) => Promise<void>;
  setTheme: (theme: Theme) => Promise<void>;
  setCacheTtl: (ms: number) => Promise<void>;
  setForceOffline: (force: boolean) => Promise<void>;
  setAutoOffline: (auto: boolean) => Promise<void>;
  hydrate: () => Promise<void>;
}

export const useSettingsStore = create<SettingsState>((set, get) => {
  const baseSettings = (): PersistedSettings => {
    const { apiUrl, refreshIntervalMs, evThreshold, theme, lastSaved } = get();
    const { cacheTtlMs, forceOffline, autoOffline } = get();
    return { apiUrl, refreshIntervalMs, evThreshold, theme, cacheTtlMs, forceOffline, autoOffline, lastSaved };
  };

  const persist = async (next: Partial<PersistedSettings>) => {
    const payload = { ...baseSettings(), ...next };
    try {
      const savedAt = await saveSecure(SETTINGS_KEY, payload);
      set({ ...payload, lastSaved: savedAt, storageStatus: 'persisted', storageMessage: undefined, initialized: true });
    } catch (error: any) {
      set({ storageStatus: 'error', storageMessage: error?.message });
    }
  };

  return {
    apiUrl: 'http://localhost:8000',
    refreshIntervalMs: 5000,
    evThreshold: 0.05,
    theme: 'dark',
    cacheTtlMs: 120000,
    forceOffline: false,
    autoOffline: true,
    storageStatus: 'loading',
    initialized: false,
    lastSaved: undefined,
    storageMessage: undefined,
    hydrate: async () => {
      set({ storageStatus: 'loading' });
      const stored = await loadSecure<PersistedSettings>(SETTINGS_KEY);
      if (stored) {
        set({ ...get(), ...stored, storageStatus: 'persisted', initialized: true });
        return;
      }
      set({ initialized: true, storageStatus: 'idle' });
    },
    setApiUrl: async (apiUrl: string) => persist({ apiUrl }),
    setRefreshInterval: async (refreshIntervalMs: number) => persist({ refreshIntervalMs }),
    setEvThreshold: async (evThreshold: number) => persist({ evThreshold }),
    setTheme: async (theme: Theme) => persist({ theme }),
    setCacheTtl: async (cacheTtlMs: number) => persist({ cacheTtlMs }),
    setForceOffline: async (forceOffline: boolean) => persist({ forceOffline }),
    setAutoOffline: async (autoOffline: boolean) => persist({ autoOffline })
  };
});
