import { useEffect, useRef, useState } from 'react';
import { websocketUrl } from '@api/client';
import { AdditionalMarketLine, Fixture, MatchEvent } from '@api/types';
import { useSettingsStore } from '@store/settings';
import { isOffline } from '@app/network';

interface LiveMatchState {
  fixtures: Fixture[];
  events: Record<string, MatchEvent[]>;
  markets: Record<string, AdditionalMarketLine[]>;
  connection: 'connecting' | 'open' | 'closed' | 'error';
  lastMessage?: number;
}

export const useLiveMatches = () => {
  const [state, setState] = useState<LiveMatchState>({
    fixtures: [],
    events: {},
    markets: {},
    connection: 'connecting'
  });
  const retryRef = useRef<NodeJS.Timeout | null>(null);
  const { forceOffline, autoOffline } = useSettingsStore();

  useEffect(() => {
    let socket: WebSocket | null = null;
    const connect = () => {
      const offline = isOffline(forceOffline, autoOffline);
      if (offline) {
        setState((prev) => ({ ...prev, connection: 'closed' }));
        return;
      }
      socket = new WebSocket(websocketUrl());
      setState((prev) => ({ ...prev, connection: 'connecting' }));

      socket.onopen = () => setState((prev) => ({ ...prev, connection: 'open' }));
      socket.onerror = () => setState((prev) => ({ ...prev, connection: 'error' }));
      socket.onclose = () => {
        setState((prev) => ({ ...prev, connection: 'closed' }));
        retryRef.current = setTimeout(connect, 1500);
      };
      socket.onmessage = (event) => {
        const payload = JSON.parse(event.data);
        setState((prev) => ({ ...prev, lastMessage: Date.now() }));

        if (payload.type === 'snapshot') {
          setState({
            fixtures: (payload.fixtures as Fixture[]) || [],
            events: (payload.events as Record<string, MatchEvent[]>) || {},
            markets: (payload.markets as Record<string, AdditionalMarketLine[]>) || {},
            connection: 'open',
            lastMessage: Date.now()
          });
        }
        if (payload.type === 'fixtures') {
          setState((prev) => ({ ...prev, fixtures: (payload.fixtures as Fixture[]) || [] }));
        }
        if (payload.type === 'event') {
          const fixtureId = payload.fixtureId as string;
          const matchEvent = payload.event as MatchEvent;
          setState((prev) => ({
            ...prev,
            events: {
              ...prev.events,
              [fixtureId]: [...(prev.events[fixtureId] || []), matchEvent]
            }
          }));
        }
        if (payload.type === 'markets') {
          setState((prev) => ({ ...prev, markets: (payload.markets as Record<string, AdditionalMarketLine[]>) || {} }));
        }
      };
    };

    connect();
    return () => {
      socket?.close();
      if (retryRef.current) clearTimeout(retryRef.current);
    };
  }, [forceOffline, autoOffline]);

  return state;
};
