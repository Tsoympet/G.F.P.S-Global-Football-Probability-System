import { useEffect, useRef, useState } from 'react';
import { useSettingsStore } from '@store/settings';

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
}

export const useQuery = <T,>(fn: () => Promise<T>, options: QueryOptions = {}): QueryState<T> & { refetch: () => void } => {
  const { refreshIntervalMs, initialized } = useSettingsStore();
  const pollMs = options.pollMs ?? refreshIntervalMs;
  const staleMs = options.staleMs ?? pollMs * 2;
  const [state, setState] = useState<QueryState<T>>({ loading: true, stale: false });
  const retryRef = useRef(0);
  const abortRef = useRef<AbortController | null>(null);

  const execute = async () => {
    if (options.enabled === false) return;
    abortRef.current?.abort();
    const aborter = new AbortController();
    abortRef.current = aborter;

    if (!state.data) {
      setState((prev) => ({ ...prev, loading: true, error: undefined }));
    }

    try {
      const data = await fn();
      if (aborter.signal.aborted) return;
      retryRef.current = 0;
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
