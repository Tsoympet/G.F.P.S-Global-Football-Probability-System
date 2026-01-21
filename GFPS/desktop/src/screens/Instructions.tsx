import { palette } from '@theme/palette';
import { useSettingsStore } from '@store/settings';
import { useAuthStore } from '@store/auth';

const Section = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <section
    style={{
      border: `1px solid ${palette.border}`,
      borderRadius: 12,
      padding: 16,
      background: palette.card,
      display: 'flex',
      flexDirection: 'column',
      gap: 8
    }}
  >
    <div style={{ color: palette.textPrimary, fontWeight: 700, fontSize: 16 }}>{title}</div>
    <div style={{ color: palette.textSecondary, fontSize: 13, lineHeight: 1.6 }}>{children}</div>
  </section>
);

export const Instructions = () => {
  const { apiUrl, refreshIntervalMs, cacheTtlMs } = useSettingsStore();
  const { token } = useAuthStore();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, maxWidth: 1100 }}>
      <div style={{ color: palette.textPrimary, fontSize: 22, fontWeight: 800 }}>How GFPS works</div>
      <div style={{ color: palette.textSecondary, fontSize: 13 }}>
        Use this guide to understand the live data pipeline, default free data feeds, and how to plug in your own API
        keys. Settings shown below reflect your current configuration.
      </div>

      <Section title="1) Live data ingestion (web scraper + WebSocket)">
        <ul style={{ paddingLeft: 16, margin: 0, display: 'grid', gap: 6 }}>
          <li>
            The desktop app opens a <strong>WebSocket</strong> to the backend to stream fixtures, odds and in-play events
            in real-time. Status is visible in Live Match Center (“Feed: connecting/open/error”).
          </li>
          <li>
            A lightweight <strong>web scraper</strong> collects live odds and market movements from supported sites. It
            runs continuously on the backend and pushes snapshots plus incremental updates over the socket.
          </li>
          <li>
            If the socket stalls, the app automatically falls back to <strong>HTTP polling</strong>. Current poll
            cadence: <code>{refreshIntervalMs} ms</code>.
          </li>
          <li>
            Cached responses are reused for a short window to reduce rate limits. Current cache TTL:{' '}
            <code>{cacheTtlMs} ms</code>.
          </li>
        </ul>
      </Section>

      <Section title="2) Default free API feed">
        <ul style={{ paddingLeft: 16, margin: 0, display: 'grid', gap: 6 }}>
          <li>
            By default the app calls the bundled <strong>free provider</strong> for fixtures, predictions and live odds
            when no custom keys are set.
          </li>
          <li>
            Base endpoint currently in use: <code>{apiUrl}</code>.
          </li>
          <li>
            Free tier limits apply: slower refresh, reduced markets, and occasional gaps. The app will show “Waiting for
            live market lines” if coverage is thin.
          </li>
        </ul>
      </Section>

      <Section title="3) Add your own API keys">
        <ol style={{ paddingLeft: 16, margin: 0, display: 'grid', gap: 6 }}>
          <li>Open <strong>Settings → Data Provider API Keys</strong>.</li>
          <li>
            Click “Get API Key” for a listed provider, sign up, and paste the key in the input. Keys are encrypted
            locally and never leave your device.
          </li>
          <li>
            Click <strong>Save API Keys</strong>. The app will start using your keys on the next fetch or socket refresh.
          </li>
          <li>
            To remove a key, clear the field and save again. The app will fall back to the default free feed
            automatically.
          </li>
        </ol>
      </Section>

      <Section title="4) Backend authentication (optional)">
        <ul style={{ paddingLeft: 16, margin: 0, display: 'grid', gap: 6 }}>
          <li>
            Some providers or private endpoints may require a bearer token. Use <strong>Settings → Desktop Login</strong>{' '}
            to authenticate.
          </li>
          <li>
            Current session: <code>{token ? 'Authenticated' : 'Guest'}</code>. Logout resets cached tokens.
          </li>
        </ul>
      </Section>

      <Section title="5) Troubleshooting tips">
        <ul style={{ paddingLeft: 16, margin: 0, display: 'grid', gap: 6 }}>
          <li>If “Feed: closed/error” appears, check internet connectivity or disable Offline Mode in Settings.</li>
          <li>Increase refresh interval if your provider enforces strict rate limits.</li>
          <li>Verify keys are valid and active at the provider dashboard if data stops updating.</li>
        </ul>
      </Section>
    </div>
  );
};
