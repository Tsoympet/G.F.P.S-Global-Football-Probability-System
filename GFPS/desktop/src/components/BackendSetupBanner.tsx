import { palette } from '@theme/palette';
import { useSettingsStore } from '@store/settings';

interface BackendSetupBannerProps {
  error: string;
}

export const BackendSetupBanner = ({ error }: BackendSetupBannerProps) => {
  const { apiUrl } = useSettingsStore();

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
        <div style={{ marginBottom: 12, color: palette.textSecondary }}>
          <strong>Option 1: Automated Scripts (Recommended)</strong>
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
            # Windows: Double-click start-backend.bat<br />
            # macOS/Linux: Run ./start-backend.sh
          </div>
          <div style={{ marginTop: 4, fontSize: 12 }}>
            These scripts automatically set up everything for you!
          </div>
        </div>
        <div style={{ color: palette.textSecondary }}>
          <strong>Option 2: Manual Setup</strong>
          <ol style={{ margin: '4px 0 0 0', paddingLeft: 20 }}>
            <li>
              Install Python dependencies:
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
                pip install -r backend/requirements.txt
              </div>
            </li>
            <li style={{ marginTop: 8 }}>
              Start the backend server:
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
          </ol>
        </div>
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
