import { useEffect, useState } from 'react';
import { websocketUrl } from '@api/client';
import { AdditionalMarketLine, Fixture, MatchEvent } from '@api/types';

interface LiveMatchState {
  fixtures: Fixture[];
  events: Record<string, MatchEvent[]>;
  markets: Record<string, AdditionalMarketLine[]>;
}

export const useLiveMatches = () => {
  const [state, setState] = useState<LiveMatchState>({ fixtures: [], events: {}, markets: {} });

  useEffect(() => {
    const socket = new WebSocket(websocketUrl());

    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.type === 'snapshot') {
        setState({
          fixtures: (payload.fixtures as Fixture[]) || [],
          events: (payload.events as Record<string, MatchEvent[]>) || {},
          markets: (payload.markets as Record<string, AdditionalMarketLine[]>) || {}
        });
      }
      if (payload.type === 'fixtures') {
        setState((prev) => ({ ...prev, fixtures: (payload.fixtures as Fixture[]) || [] }));
      }
      if (payload.type === 'event') {
        const fixtureId = payload.fixtureId as string;
        const matchEvent = payload.event as MatchEvent;
        setState((prev) => ({
          fixtures: prev.fixtures,
          events: {
            ...prev.events,
            [fixtureId]: [...(prev.events[fixtureId] || []), matchEvent]
          },
          markets: prev.markets
        }));
      }
      if (payload.type === 'markets') {
        setState((prev) => ({ ...prev, markets: (payload.markets as Record<string, AdditionalMarketLine[]>) || {} }));
      }
    };

    return () => socket.close();
  }, []);

  return state;
};
