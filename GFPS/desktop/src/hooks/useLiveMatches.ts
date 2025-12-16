import { useEffect, useState } from 'react';
import { websocketUrl } from '@api/client';
import { Fixture, MatchEvent } from '@api/types';

interface LiveMatchState {
  fixtures: Fixture[];
  events: Record<string, MatchEvent[]>;
}

export const useLiveMatches = () => {
  const [state, setState] = useState<LiveMatchState>({ fixtures: [], events: {} });

  useEffect(() => {
    const socket = new WebSocket(websocketUrl());

    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.type === 'fixtures') {
        setState((prev) => ({ ...prev, fixtures: payload.data as Fixture[] }));
      }
      if (payload.type === 'event') {
        const { fixtureId, event: matchEvent } = payload.data as {
          fixtureId: string;
          event: MatchEvent;
        };
        setState((prev) => ({
          fixtures: prev.fixtures,
          events: {
            ...prev.events,
            [fixtureId]: [...(prev.events[fixtureId] || []), matchEvent]
          }
        }));
      }
    };

    return () => socket.close();
  }, []);

  return state;
};
