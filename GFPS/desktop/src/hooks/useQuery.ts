import { useEffect, useRef, useState } from 'react';
import { useSettingsStore } from '@store/settings';
import { loadCached, saveCached } from '@app/cache';
import { isOffline } from '@app/network';

interface QueryState<T> {
  data?: T;
  loading: boolean;
  error?: string;
  lastUpdated?: number;
  stale: boolean;
}

interface QueryOptions {
  deps?: unknown[];
  pollMs?: number;
  staleMs?: number;
  enabled?: boolean;
  retry?: number;
  cacheKey?: string;
  ttlMs?: number;
  useCache?: boolean;
}

export const useQuery = <T,>(fn: () => Promise<T>, options: QueryOptions = {}): QueryState<T> & { refetch: () => void } => {
  const { refreshIntervalMs, initialized, cacheTtlMs, forceOffline, autoOffline } = useSettingsStore();
  const pollMs = options.pollMs ?? refreshIntervalMs;
  const staleMs = options.staleMs ?? pollMs * 2;
  const [state, setState] = useState<QueryState<T>>({ loading: true, stale: false });
  const retryRef = useRef(0);
  const abortRef = useRef<AbortController | null>(null);
  const cacheKey = options.cacheKey;
  const ttlMs = options.ttlMs ?? cacheTtlMs;

  useEffect(() => {
    const bootstrap = async () => {
      if (!cacheKey || options.useCache === false) return;
      const cached = await loadCached<T>(cacheKey, ttlMs);
      if (cached?.data) {
        setState((prev) => ({
          ...prev,
          data: cached.data,
          loading: false,
          stale: prev.stale || cached.stale,
          lastUpdated: cached.timestamp
        }));
      }
    };
    bootstrap();
  }, [cacheKey, ttlMs, options.useCache]);

  const execute = async () => {
    if (options.enabled === false) return;
    abortRef.current?.abort();
    const aborter = new AbortController();
    abortRef.current = aborter;

    if (!state.data) {
      setState((prev) => ({ ...prev, loading: true, error: undefined }));
    }

    try {
      const cached = cacheKey && options.useCache !== false ? await loadCached<T>(cacheKey, ttlMs) : undefined;
      if (isOffline(forceOffline, autoOffline) && cached?.data) {
        setState({
          loading: false,
          data: cached.data,
          error: 'Offline — using cached data',
          lastUpdated: cached.timestamp,
          stale: true
        });
        return;
      }
      const data = await fn();
      if (aborter.signal.aborted) return;
      retryRef.current = 0;
      if (cacheKey && options.useCache !== false) {
        await saveCached(cacheKey, data, ttlMs);
      }
      setState({ loading: false, data, error: undefined, lastUpdated: Date.now(), stale: false });
    } catch (error: any) {
      if (aborter.signal.aborted) return;
      const retries = options.retry ?? 1;
      if (retryRef.current < retries) {
        retryRef.current += 1;
        setTimeout(execute, 500);
        return;
      }
      setState((prev) => ({ ...prev, loading: false, error: error?.message || 'Request failed' }));
    }
  };

  useEffect(() => {
    if (!initialized && pollMs) return;
    let mounted = true;
    execute();

    let timer: NodeJS.Timeout | null = null;
    if (pollMs) {
      timer = setInterval(() => mounted && execute(), pollMs);
    }

    return () => {
      mounted = false;
      if (timer) clearInterval(timer);
      abortRef.current?.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialized, pollMs, ...(options.deps || [])]);

  useEffect(() => {
    if (!state.lastUpdated) return;
    const timer = setTimeout(
      () => setState((prev) => ({ ...prev, stale: true })),
      staleMs ?? refreshIntervalMs * 2
    );
    return () => clearTimeout(timer);
  }, [state.lastUpdated, staleMs, refreshIntervalMs]);

  return { ...state, refetch: execute };
};
