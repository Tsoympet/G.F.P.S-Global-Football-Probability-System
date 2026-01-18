import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useLiveMatches } from '@hooks/useLiveMatches';
import { useSettingsStore } from '@store/settings';

// Mock WebSocket
class MockWebSocket {
  onopen: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  
  close() {
    // Mock close
  }
}

describe('useLiveMatches - Security', () => {
  let mockWebSocket: MockWebSocket;
  
  beforeEach(() => {
    // Reset settings store
    useSettingsStore.setState({
      apiUrl: 'http://localhost:8000',
      refreshIntervalMs: 5000,
      evThreshold: 0.05,
      theme: 'dark',
      cacheTtlMs: 120000,
      forceOffline: false,
      autoOffline: false,
      storageStatus: 'idle',
      initialized: true
    });
    
    // Mock WebSocket
    mockWebSocket = new MockWebSocket();
    global.WebSocket = vi.fn(() => mockWebSocket) as any;
  });
  
  afterEach(() => {
    vi.clearAllMocks();
  });
  
  it('should prevent prototype pollution via __proto__ in event messages', async () => {
    const { result } = renderHook(() => useLiveMatches());
    
    // Simulate WebSocket connection
    if (mockWebSocket.onopen) {
      mockWebSocket.onopen();
    }
    
    await waitFor(() => {
      expect(result.current.connection).toBe('open');
    });
    
    // Attempt prototype pollution attack via event message
    const maliciousPayload = {
      type: 'event',
      fixtureId: '__proto__',
      event: {
        minute: 45,
        description: 'Malicious event',
        type: 'goal'
      }
    };
    
    if (mockWebSocket.onmessage) {
      mockWebSocket.onmessage({ data: JSON.stringify(maliciousPayload) });
    }
    
    await waitFor(() => {
      // The key should be sanitized to "$__proto__" instead of "__proto__"
      expect(result.current.events['$__proto__']).toBeDefined();
      expect(result.current.events['__proto__']).toBeUndefined();
      expect(result.current.events['$__proto__']).toHaveLength(1);
    });
    
    // Verify prototype is not polluted
    const testObj: any = {};
    expect(testObj.polluted).toBeUndefined();
  });
  
  it('should prevent prototype pollution via constructor in event messages', async () => {
    const { result } = renderHook(() => useLiveMatches());
    
    if (mockWebSocket.onopen) {
      mockWebSocket.onopen();
    }
    
    await waitFor(() => {
      expect(result.current.connection).toBe('open');
    });
    
    const maliciousPayload = {
      type: 'event',
      fixtureId: 'constructor',
      event: {
        minute: 45,
        description: 'Malicious event',
        type: 'goal'
      }
    };
    
    if (mockWebSocket.onmessage) {
      mockWebSocket.onmessage({ data: JSON.stringify(maliciousPayload) });
    }
    
    await waitFor(() => {
      expect(result.current.events['$constructor']).toBeDefined();
      expect(result.current.events['$constructor']).toHaveLength(1);
    });
  });
  
  it('should sanitize snapshot event keys', async () => {
    const { result } = renderHook(() => useLiveMatches());
    
    if (mockWebSocket.onopen) {
      mockWebSocket.onopen();
    }
    
    const snapshotPayload = {
      type: 'snapshot',
      fixtures: [],
      events: {
        '__proto__': [{
          minute: 10,
          description: 'Test',
          type: 'goal'
        }],
        'validId123': [{
          minute: 20,
          description: 'Valid event',
          type: 'goal'
        }]
      },
      markets: {}
    };
    
    if (mockWebSocket.onmessage) {
      mockWebSocket.onmessage({ data: JSON.stringify(snapshotPayload) });
    }
    
    await waitFor(() => {
      // Verify keys are sanitized
      expect(result.current.events['$__proto__']).toBeDefined();
      expect(result.current.events['$validId123']).toBeDefined();
      expect(result.current.events['__proto__']).toBeUndefined();
      expect(result.current.events['validId123']).toBeUndefined();
    });
  });
  
  it('should sanitize market keys in snapshot', async () => {
    const { result } = renderHook(() => useLiveMatches());
    
    if (mockWebSocket.onopen) {
      mockWebSocket.onopen();
    }
    
    const snapshotPayload = {
      type: 'snapshot',
      fixtures: [],
      events: {},
      markets: {
        '__proto__': [{
          fixtureId: 'test',
          label: 'Over 2.5',
          type: 'total',
          line: '2.5',
          over: 1.9
        }],
        'validId456': [{
          fixtureId: 'test',
          label: 'Over 2.5',
          type: 'total',
          line: '2.5',
          over: 1.9
        }]
      }
    };
    
    if (mockWebSocket.onmessage) {
      mockWebSocket.onmessage({ data: JSON.stringify(snapshotPayload) });
    }
    
    await waitFor(() => {
      expect(result.current.markets['$__proto__']).toBeDefined();
      expect(result.current.markets['$validId456']).toBeDefined();
      expect(result.current.markets['__proto__']).toBeUndefined();
      expect(result.current.markets['validId456']).toBeUndefined();
    });
  });
  
  it('should handle normal fixture IDs correctly', async () => {
    const { result } = renderHook(() => useLiveMatches());
    
    if (mockWebSocket.onopen) {
      mockWebSocket.onopen();
    }
    
    await waitFor(() => {
      expect(result.current.connection).toBe('open');
    });
    
    const normalPayload = {
      type: 'event',
      fixtureId: 'match-12345',
      event: {
        minute: 30,
        description: 'Goal by Home Team',
        type: 'goal'
      }
    };
    
    if (mockWebSocket.onmessage) {
      mockWebSocket.onmessage({ data: JSON.stringify(normalPayload) });
    }
    
    await waitFor(() => {
      expect(result.current.events['$match-12345']).toBeDefined();
      expect(result.current.events['$match-12345']).toHaveLength(1);
      expect(result.current.events['$match-12345'][0].description).toBe('Goal by Home Team');
    });
  });
});
