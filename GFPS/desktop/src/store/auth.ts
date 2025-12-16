import { create } from 'zustand';
import { useSettingsStore } from './settings';

interface Profile {
  email: string;
  display_name?: string;
  avatar_url?: string;
  role?: string;
}

interface AuthState {
  token: string | null;
  profile: Profile | null;
  status: 'idle' | 'loading' | 'error';
  error?: string;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const buildUrl = (path: string) => {
  const baseUrl = useSettingsStore.getState().apiUrl.replace(/\/$/, '');
  return `${baseUrl}${path}`;
};

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  profile: null,
  status: 'idle',
  error: undefined,
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
    } catch (err: any) {
      set({ status: 'error', error: err.message || 'Login failed' });
    }
  },
  logout: () => set({ token: null, profile: null, status: 'idle', error: undefined })
}));
