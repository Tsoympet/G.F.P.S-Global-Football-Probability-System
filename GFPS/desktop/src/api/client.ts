import { useAuthStore } from '@store/auth';
import { useSettingsStore } from '@store/settings';
import { loadCached, saveCached } from '@app/cache';
import { isOffline } from '@app/network';
import { Fixture, LiveOddsPayload, ModelInfo, PipelineStatus, Prediction, ValueBet } from './types';

const jsonHeaders = { 'Content-Type': 'application/json' };
const UNKNOWN_HOME = 'Home';
const UNKNOWN_AWAY = 'Away';
const UNKNOWN_LEAGUE = 'Unknown';

const buildUrl = (path: string) => {
  const baseUrl = useSettingsStore.getState().apiUrl.replace(/\/$/, '');
  return `${baseUrl}${path}`;
};

const authHeaders = () => {
  const token = useAuthStore.getState().token;
  return token ? { Authorization: `Bearer ${token}` } : {};
};

async function get<T>(path: string, cacheKey?: string): Promise<T> {
  const { cacheTtlMs, forceOffline, autoOffline } = useSettingsStore.getState();
  const cached = cacheKey ? await loadCached<T>(cacheKey, cacheTtlMs) : undefined;
  const offline = isOffline(forceOffline, autoOffline);
  if (offline && cached?.data) return cached.data;

  const res = await fetch(buildUrl(path), { headers: { ...authHeaders() } });
  if (!res.ok) {
    if (cached?.data) return cached.data;
    throw new Error(`Request failed: ${res.status}`);
  }
  const data = await res.json();
  if (cacheKey) await saveCached(cacheKey, data, cacheTtlMs);
  return data;
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(buildUrl(path), {
    method: 'POST',
    headers: { ...jsonHeaders, ...authHeaders() },
    body: body ? JSON.stringify(body) : undefined
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export const api = {
  fixtures: async () => {
    try {
      return await get<Fixture[]>('/fixtures', 'fixtures');
    } catch {
      // Fallback: derive minimal fixture rows from predictions when dedicated fixtures endpoint is unavailable.
      const predictions = await get<Prediction[]>('/predictions', 'predictions');
      return predictions.map((p) => ({
        id: p.fixtureId,
        homeTeam: p.homeTeam || UNKNOWN_HOME,
        awayTeam: p.awayTeam || UNKNOWN_AWAY,
        league: p.league || UNKNOWN_LEAGUE,
        startTime: p.startTime || new Date().toISOString(),
        status:
          p.status ||
          (p.startTime && new Date(p.startTime) < new Date() ? ('finished' as const) : ('scheduled' as const))
      }));
    }
  },
  odds: async () => {
    try {
      return await get<LiveOddsPayload>('/odds', 'odds');
    } catch {
      return get<LiveOddsPayload>('/live-odds', 'odds');
    }
  },
  predictions: () => get<Prediction[]>('/predictions', 'predictions'),
  valueBets: async (minEv?: number) => {
    const path = `/value${minEv ? `?min_ev=${minEv}` : ''}`;
    try {
      return await get<ValueBet[]>(path, `value-bets-${minEv ?? 'all'}`);
    } catch {
      return get<ValueBet[]>(`/value-bets${minEv ? `?min_ev=${minEv}` : ''}`, `value-bets-${minEv ?? 'all'}`);
    }
  },
  trainModel: () => post<{ message: string }>('/ml/train'),
  models: () => get<ModelInfo[]>('/ml/models'),
  activateModel: (version: string) => post<{ message: string }>(`/ml/activate/${version}`),
  pipelineStatus: () => get<PipelineStatus>('/pipeline/status'),
  health: () => get<{ ok: boolean; uptime_sec: number; services: Record<string, { status: string }> }>('/health'),
  analyzeBetSlip: (request: any) => post<any>('/analysis/betslip', request)
};

export const websocketUrl = () => {
  const apiUrl = useSettingsStore.getState().apiUrl;
  const host = apiUrl.replace('http://', '').replace('https://', '');
  const protocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
  return `${protocol}://${host}/ws/live-matches`;
};
