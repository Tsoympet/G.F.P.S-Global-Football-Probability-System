import { useSettingsStore } from '@store/settings';
import { palette } from '@theme/palette';
import { useState } from 'react';

export const Settings = () => {
  const { apiUrl, refreshIntervalMs, setApiUrl, setRefreshInterval } = useSettingsStore();
  const [urlInput, setUrlInput] = useState(apiUrl);
  const [refreshInput, setRefreshInput] = useState(refreshIntervalMs);

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
    </section>
  );
};
