import { loadSecure, saveSecure, clearSecure } from '@app/secureStorage';
import { create } from 'zustand';
import { useSettingsStore } from './settings';

interface Profile {
  email: string;
  display_name?: string;
  avatar_url?: string;
}

interface AuthState {
  token: string | null;
  profile: Profile | null;
  status: 'idle' | 'loading' | 'error';
  error?: string;
  initialized: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  hydrate: () => Promise<void>;
}

const buildUrl = (path: string) => {
  const baseUrl = useSettingsStore.getState().apiUrl.replace(/\/$/, '');
  return `${baseUrl}${path}`;
};

const AUTH_KEY = 'gfps_auth';

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  profile: null,
  status: 'idle',
  error: undefined,
  initialized: false,
  hydrate: async () => {
    const stored = await loadSecure<{ token: string; profile: Profile }>(AUTH_KEY);
    if (stored?.token) {
      set({ token: stored.token, profile: stored.profile, initialized: true });
      return;
    }
    set({ initialized: true });
  },
  login: async (email: string, password: string) => {
    set({ status: 'loading', error: undefined });
    try {
      const res = await fetch(buildUrl('/auth/login'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (!res.ok) throw new Error(`Login failed (${res.status})`);
      const data = await res.json();
      set({ token: data.token, profile: data.profile, status: 'idle' });
      await saveSecure(AUTH_KEY, { token: data.token, profile: data.profile });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      set({ status: 'error', error: errorMessage });
    }
  },
  logout: () => {
    clearSecure(AUTH_KEY);
    set({ token: null, profile: null, status: 'idle', error: undefined });
  }
}));
