import { useSettingsStore } from '@store/settings';
import { useAuthStore } from '@store/auth';
import { palette } from '@theme/palette';
import { useState, useEffect } from 'react';
import { loadSecure, saveSecure } from '@app/secureStorage';

export const Settings = () => {
  const {
    apiUrl,
    refreshIntervalMs,
    evThreshold,
    theme,
    cacheTtlMs,
    forceOffline,
    autoOffline,
    lastSaved,
    storageStatus,
    storageMessage,
    setApiUrl,
    setRefreshInterval,
    setEvThreshold,
    setTheme,
    setCacheTtl,
    setForceOffline,
    setAutoOffline
  } = useSettingsStore();
  const [urlInput, setUrlInput] = useState(apiUrl);
  const [refreshInput, setRefreshInput] = useState(refreshIntervalMs);
  const [ttlInput, setTtlInput] = useState(cacheTtlMs);
  const { token, profile, status, error, login, logout } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // API Provider credentials
  const [apiProviders, setApiProviders] = useState<Record<string, string>>({});
  const [apiFootballKey, setApiFootballKey] = useState('');
  const [footballDataKey, setFootballDataKey] = useState('');
  const [oddsMatrixKey, setOddsMatrixKey] = useState('');

  useEffect(() => {
    loadSecure<Record<string, string>>('gfps_api_providers').then((data) => {
      if (data) {
        setApiProviders(data);
        setApiFootballKey(data['api-football'] || '');
        setFootballDataKey(data['football-data'] || '');
        setOddsMatrixKey(data['odds-matrix'] || '');
      }
    });
  }, []);

  const saveApiKeys = async () => {
    const providers: Record<string, string> = {};
    if (apiFootballKey) providers['api-football'] = apiFootballKey;
    if (footballDataKey) providers['football-data'] = footballDataKey;
    if (oddsMatrixKey) providers['odds-matrix'] = oddsMatrixKey;
    await saveSecure('gfps_api_providers', providers);
    setApiProviders(providers);
  };

  const openProviderSignup = (url: string) => {
    window.open(url, '_blank');
  };

  return (
    <section
      style={{
        border: `1px solid ${palette.border}`,
        borderRadius: 14,
        background: palette.cardElevated,
        padding: 16,
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
        maxWidth: 720
      }}
    >
      <div style={{ color: palette.textPrimary, fontSize: 20, fontWeight: 700 }}>Settings</div>
      <div style={{ color: palette.textSecondary, fontSize: 12 }}>
        Secure settings are encrypted at rest and stored locally only. Last saved: {lastSaved || 'pending'} • Status:{' '}
        {storageStatus}
      </div>
      {storageMessage && <div style={{ color: palette.danger }}>{storageMessage}</div>}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <label style={{ color: palette.textSecondary, fontSize: 14 }}>Backend API URL</label>
        <input
          value={urlInput}
          onChange={(e) => setUrlInput(e.target.value)}
          style={{
            background: palette.card,
            border: `1px solid ${palette.border}`,
            color: palette.textPrimary,
            padding: '12px 14px',
            borderRadius: 10
          }}
        />
        <button
          onClick={() => setApiUrl(urlInput)}
          style={{
            alignSelf: 'flex-start',
            background: 'linear-gradient(90deg, #1f9ae5, #0fd7a1)',
            color: '#0b0f1a',
            border: 'none',
            padding: '10px 14px',
            borderRadius: 10,
            fontWeight: 700,
            cursor: 'pointer'
          }}
        >
          Save API URL
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <label style={{ color: palette.textSecondary, fontSize: 14 }}>Refresh Interval (ms)</label>
        <input
          type="number"
          value={refreshInput}
          onChange={(e) => setRefreshInput(Number(e.target.value))}
          style={{
            background: palette.card,
            border: `1px solid ${palette.border}`,
            color: palette.textPrimary,
            padding: '12px 14px',
            borderRadius: 10
          }}
        />
        <button
          onClick={() => setRefreshInterval(refreshInput)}
          style={{
            alignSelf: 'flex-start',
            background: 'transparent',
            border: `1px solid ${palette.border}`,
            color: palette.textPrimary,
            padding: '10px 14px',
            borderRadius: 10,
            fontWeight: 700,
            cursor: 'pointer'
          }}
        >
          Update Interval
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 12 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <label style={{ color: palette.textSecondary, fontSize: 14 }}>EV Threshold (%)</label>
          <input
            type="range"
            min={1}
            max={20}
            value={Math.round(evThreshold * 100)}
            onChange={(e) => setEvThreshold(Number(e.target.value) / 100)}
          />
          <div style={{ color: palette.textSecondary, fontSize: 13 }}>
            Current EV floor: {(evThreshold * 100).toFixed(1)}%
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <label style={{ color: palette.textSecondary, fontSize: 14 }}>Theme</label>
          <select
            value={theme}
            onChange={(e) => setTheme(e.target.value as 'dark' | 'contrast')}
            style={{
              background: palette.card,
              border: `1px solid ${palette.border}`,
              color: palette.textPrimary,
              padding: '12px 14px',
              borderRadius: 10
            }}
          >
            <option value="dark">Dark analytics</option>
            <option value="contrast">High contrast</option>
          </select>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 12 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <label style={{ color: palette.textSecondary, fontSize: 14 }}>Cache TTL (ms)</label>
          <input
            type="number"
            value={ttlInput}
            onChange={(e) => setTtlInput(Number(e.target.value))}
            style={{
              background: palette.card,
              border: `1px solid ${palette.border}`,
              color: palette.textPrimary,
              padding: '12px 14px',
              borderRadius: 10
            }}
          />
          <button
            onClick={() => setCacheTtl(ttlInput)}
            style={{
              alignSelf: 'flex-start',
              background: 'transparent',
              border: `1px solid ${palette.border}`,
              color: palette.textPrimary,
              padding: '10px 14px',
              borderRadius: 10,
              fontWeight: 700,
              cursor: 'pointer'
            }}
          >
            Update Cache TTL
          </button>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <label style={{ color: palette.textSecondary, fontSize: 14 }}>Offline mode</label>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <input
              type="checkbox"
              checked={forceOffline}
              onChange={(e) => setForceOffline(e.target.checked)}
            />
            <span style={{ color: palette.textSecondary, fontSize: 13 }}>Force offline (manual)</span>
          </div>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <input
              type="checkbox"
              checked={autoOffline}
              onChange={(e) => setAutoOffline(e.target.checked)}
            />
            <span style={{ color: palette.textSecondary, fontSize: 13 }}>Auto-detect offline</span>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <label style={{ color: palette.textSecondary, fontSize: 14 }}>Desktop Login</label>
        <input
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          style={{
            background: palette.card,
            border: `1px solid ${palette.border}`,
            color: palette.textPrimary,
            padding: '12px 14px',
            borderRadius: 10
          }}
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
          style={{
            background: palette.card,
            border: `1px solid ${palette.border}`,
            color: palette.textPrimary,
            padding: '12px 14px',
            borderRadius: 10
          }}
        />
        <div style={{ display: 'flex', gap: 12 }}>
          <button
            onClick={() => login(email, password)}
            disabled={status === 'loading'}
            style={{
              background: 'linear-gradient(90deg, #1f9ae5, #0fd7a1)',
              color: '#0b0f1a',
              border: 'none',
              padding: '10px 14px',
              borderRadius: 10,
              fontWeight: 700,
              cursor: 'pointer'
            }}
          >
            {status === 'loading' ? 'Logging in...' : 'Login'}
          </button>
          {token && (
            <button
              onClick={logout}
              style={{
                background: 'transparent',
                border: `1px solid ${palette.border}`,
                color: palette.textPrimary,
                padding: '10px 14px',
                borderRadius: 10,
                fontWeight: 700,
                cursor: 'pointer'
              }}
            >
              Logout
            </button>
          )}
        </div>
        {profile && (
          <div style={{ color: palette.textSecondary, fontSize: 13 }}>
            Logged in as {profile.email}
          </div>
        )}
        {error && <div style={{ color: '#ef4444' }}>{error}</div>}
      </div>

      {/* API Provider Credentials Section */}
      <div style={{ 
        borderTop: `1px solid ${palette.border}`, 
        paddingTop: 16, 
        display: 'flex', 
        flexDirection: 'column', 
        gap: 10 
      }}>
        <div style={{ color: palette.textPrimary, fontSize: 18, fontWeight: 700 }}>
          Data Provider API Keys
        </div>
        <div style={{ color: palette.textSecondary, fontSize: 13 }}>
          Connect your own API subscriptions. Click "Get API Key" to sign up at the provider's website, 
          then paste your key below. Your credentials are encrypted and stored locally.
        </div>

        {/* API-Football */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <label style={{ color: palette.textSecondary, fontSize: 14, flex: 1 }}>
              API-Football (Premium odds & live data)
            </label>
            <button
              onClick={() => openProviderSignup('https://www.api-football.com/pricing')}
              style={{
                background: 'transparent',
                border: `1px solid ${palette.border}`,
                color: palette.textPrimary,
                padding: '6px 12px',
                borderRadius: 8,
                fontSize: 12,
                cursor: 'pointer'
              }}
            >
              Get API Key →
            </button>
          </div>
          <input
            type="password"
            value={apiFootballKey}
            onChange={(e) => setApiFootballKey(e.target.value)}
            placeholder="Paste your API-Football key here"
            style={{
              background: palette.card,
              border: `1px solid ${palette.border}`,
              color: palette.textPrimary,
              padding: '10px 12px',
              borderRadius: 8,
              fontSize: 13
            }}
          />
        </div>

        {/* Football-Data.org */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <label style={{ color: palette.textSecondary, fontSize: 14, flex: 1 }}>
              Football-Data.org (Free tier available)
            </label>
            <button
              onClick={() => openProviderSignup('https://www.football-data.org/client/register')}
              style={{
                background: 'transparent',
                border: `1px solid ${palette.border}`,
                color: palette.textPrimary,
                padding: '6px 12px',
                borderRadius: 8,
                fontSize: 12,
                cursor: 'pointer'
              }}
            >
              Get API Key →
            </button>
          </div>
          <input
            type="password"
            value={footballDataKey}
            onChange={(e) => setFootballDataKey(e.target.value)}
            placeholder="Paste your Football-Data.org key here"
            style={{
              background: palette.card,
              border: `1px solid ${palette.border}`,
              color: palette.textPrimary,
              padding: '10px 12px',
              borderRadius: 8,
              fontSize: 13
            }}
          />
        </div>

        {/* Odds Matrix */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <label style={{ color: palette.textSecondary, fontSize: 14, flex: 1 }}>
              Odds Matrix (Odds comparison data)
            </label>
            <button
              onClick={() => openProviderSignup('https://oddsmatrix.com/')}
              style={{
                background: 'transparent',
                border: `1px solid ${palette.border}`,
                color: palette.textPrimary,
                padding: '6px 12px',
                borderRadius: 8,
                fontSize: 12,
                cursor: 'pointer'
              }}
            >
              Get API Key →
            </button>
          </div>
          <input
            type="password"
            value={oddsMatrixKey}
            onChange={(e) => setOddsMatrixKey(e.target.value)}
            placeholder="Paste your Odds Matrix key here"
            style={{
              background: palette.card,
              border: `1px solid ${palette.border}`,
              color: palette.textPrimary,
              padding: '10px 12px',
              borderRadius: 8,
              fontSize: 13
            }}
          />
        </div>

        <button
          onClick={saveApiKeys}
          style={{
            alignSelf: 'flex-start',
            background: 'linear-gradient(90deg, #1f9ae5, #0fd7a1)',
            color: '#0b0f1a',
            border: 'none',
            padding: '10px 14px',
            borderRadius: 10,
            fontWeight: 700,
            cursor: 'pointer'
          }}
        >
          Save API Keys
        </button>
        {Object.keys(apiProviders).length > 0 && (
          <div style={{ color: palette.textSecondary, fontSize: 13 }}>
            {Object.keys(apiProviders).length} provider(s) configured
          </div>
        )}
      </div>
    </section>
  );
};
