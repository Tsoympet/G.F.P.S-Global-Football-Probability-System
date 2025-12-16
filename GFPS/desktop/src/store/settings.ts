import { create } from 'zustand';

export interface SettingsState {
  apiUrl: string;
  refreshIntervalMs: number;
  theme: 'dark';
  setApiUrl: (apiUrl: string) => void;
  setRefreshInterval: (ms: number) => void;
}

export const useSettingsStore = create<SettingsState>((set) => ({
  apiUrl: 'http://localhost:8000',
  refreshIntervalMs: 5000,
  theme: 'dark',
  setApiUrl: (apiUrl) => set({ apiUrl }),
  setRefreshInterval: (refreshIntervalMs) => set({ refreshIntervalMs })
}));
