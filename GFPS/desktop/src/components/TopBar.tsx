import { palette } from '@theme/palette';
import { useSettingsStore } from '@store/settings';

export const TopBar = () => {
  const { apiUrl } = useSettingsStore();
  const now = new Date();
  return (
    <header
      style={{
        height: 64,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 20px',
        borderBottom: `1px solid ${palette.border}`,
        background: 'rgba(17,24,39,0.6)',
        backdropFilter: 'blur(10px)'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <div
          style={{
            width: 10,
            height: 10,
            borderRadius: '50%',
            background: '#22c55e',
            boxShadow: '0 0 10px #22c55e'
          }}
        />
        <div style={{ color: palette.textPrimary, fontWeight: 600 }}>Live link: {apiUrl}</div>
      </div>
      <div style={{ color: palette.textSecondary, fontSize: 14 }}>{now.toUTCString()}</div>
    </header>
  );
};
