import { useSettingsStore } from '@store/settings';
import { Fixture, LiveOddsRow, ModelInfo, Prediction, ValueBet } from './types';

const jsonHeaders = { 'Content-Type': 'application/json' };

const buildUrl = (path: string) => {
  const baseUrl = useSettingsStore.getState().apiUrl.replace(/\/$/, '');
  return `${baseUrl}${path}`;
};

async function get<T>(path: string): Promise<T> {
  const res = await fetch(buildUrl(path));
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(buildUrl(path), {
    method: 'POST',
    headers: jsonHeaders,
    body: body ? JSON.stringify(body) : undefined
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export const api = {
  fixtures: () => get<Fixture[]>('/fixtures'),
  liveOdds: () => get<LiveOddsRow[]>('/live-odds'),
  predictions: () => get<Prediction[]>('/predictions'),
  valueBets: () => get<ValueBet[]>('/value-bets'),
  trainModel: () => post<{ message: string }>('/ml/train'),
  models: () => get<ModelInfo[]>('/ml/models'),
  activateModel: (version: string) => post<{ message: string }>(`/ml/activate/${version}`)
};

export const websocketUrl = () => {
  const apiUrl = useSettingsStore.getState().apiUrl;
  const host = apiUrl.replace('http://', '').replace('https://', '');
  const protocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
  return `${protocol}://${host}/ws/live-matches`;
};
