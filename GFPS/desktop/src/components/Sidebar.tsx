import { useNavigationStore, Section } from '@store/navigation';
import { palette } from '@theme/palette';
import clsx from 'clsx';

const items: { label: Section; icon: string }[] = [
  { label: 'Dashboard', icon: '📊' },
  { label: 'Live Match Center', icon: '📡' },
  { label: 'Value Bets (EV+)', icon: '💹' },
  { label: 'Models & Training', icon: '🧠' },
  { label: 'Settings', icon: '⚙️' }
];

export const Sidebar = () => {
  const { section, setSection } = useNavigationStore();

  return (
    <aside
      style={{
        width: 240,
        background: palette.card,
        borderRight: `1px solid ${palette.border}`,
        display: 'flex',
        flexDirection: 'column',
        padding: '20px 16px',
        gap: 8
      }}
    >
      <div style={{ color: palette.textSecondary, fontSize: 12, letterSpacing: 1 }}>GFPS DESKTOP</div>
      <div style={{ color: palette.textPrimary, fontSize: 18, fontWeight: 700, marginBottom: 16 }}>
        Global Football Probability System
      </div>
      <nav style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {items.map(({ label, icon }) => (
          <button
            key={label}
            onClick={() => setSection(label)}
            className={clsx('nav-item', { active: section === label })}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              padding: '12px 14px',
              borderRadius: 10,
              border: `1px solid ${palette.border}`,
              background:
                section === label
                  ? `linear-gradient(90deg, rgba(31,154,229,0.25), rgba(15,215,161,0.18))`
                  : palette.card,
              color: palette.textPrimary,
              cursor: 'pointer'
            }}
          >
            <span style={{ fontSize: 18 }}>{icon}</span>
            <span style={{ fontWeight: 600 }}>{label}</span>
          </button>
        ))}
      </nav>
      <div style={{ marginTop: 'auto', fontSize: 12, color: palette.textSecondary }}>
        Desktop-only • Connected to FastAPI backend
      </div>
    </aside>
  );
};
