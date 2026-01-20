import { palette } from '@theme/palette';
import { useSettingsStore } from '@store/settings';
import { useNavigationStore } from '@store/navigation';

interface BackendSetupBannerProps {
  error: string;
}

export const BackendSetupBanner = ({ error }: BackendSetupBannerProps) => {
  const { apiUrl } = useSettingsStore();
  const { setSection } = useNavigationStore();

  const isConnectionError = error.includes('failed') || error.includes('Failed');

  if (!isConnectionError) {
    return (
      <div style={{ color: palette.danger, fontSize: 13 }}>
        {error} — automatic retries enabled.
      </div>
    );
  }

  return (
    <div
      style={{
        border: `1px solid ${palette.danger}`,
        borderRadius: 8,
        padding: 16,
        background: `${palette.danger}15`,
        display: 'flex',
        flexDirection: 'column',
        gap: 12
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontSize: 20 }}>⚠️</span>
        <div style={{ flex: 1 }}>
          <div style={{ color: palette.danger, fontWeight: 700, fontSize: 16 }}>
            Backend API Not Available
          </div>
          <div style={{ color: palette.textSecondary, fontSize: 13, marginTop: 4 }}>
            Cannot connect to {apiUrl}
          </div>
        </div>
      </div>

      <div
        style={{
          border: `1px solid ${palette.border}`,
          borderRadius: 6,
          padding: 12,
          background: palette.card,
          fontSize: 13,
          lineHeight: 1.6
        }}
      >
        <div style={{ color: palette.textPrimary, fontWeight: 600, marginBottom: 8 }}>
          📋 Quick Setup Steps:
        </div>
        <ol style={{ margin: 0, paddingLeft: 20, color: palette.textSecondary }}>
          <li>
            <strong>Start the backend server:</strong>
            <div
              style={{
                background: palette.background,
                padding: 8,
                borderRadius: 4,
                marginTop: 4,
                fontFamily: 'monospace',
                fontSize: 12
              }}
            >
              # Install Python dependencies (first time only)<br />
              pip install -r backend/requirements.txt<br />
              <br />
              # Start the backend server<br />
              uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
            </div>
          </li>
          <li style={{ marginTop: 8 }}>
            <strong>Verify backend is running:</strong> Visit{' '}
            <a
              href={`${apiUrl}/health`}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: palette.primary }}
            >
              {apiUrl}/health
            </a>{' '}
            in your browser
          </li>
          <li style={{ marginTop: 8 }}>
            <strong>Configure API endpoint:</strong> Go to{' '}
            <button
              onClick={() => setSection('Settings')}
              style={{
                background: 'transparent',
                border: 'none',
                color: palette.primary,
                cursor: 'pointer',
                textDecoration: 'underline',
                padding: 0,
                font: 'inherit'
              }}
            >
              Settings
            </button>{' '}
            if using a different URL
          </li>
        </ol>
      </div>

      <div style={{ color: palette.textSecondary, fontSize: 12, marginTop: 4 }}>
        💡 <strong>Need help?</strong> See the{' '}
        <a
          href="https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System#-getting-started-locally"
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: palette.primary }}
        >
          Getting Started Guide
        </a>{' '}
        for detailed setup instructions.
      </div>
    </div>
  );
};
