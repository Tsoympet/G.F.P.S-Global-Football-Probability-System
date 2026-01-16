import { buildBookmakerVerdict, BookmakerContext, BookmakerVerdict } from '@app/bookmakerAi';
import { palette } from '@theme/palette';

interface Props {
  context: BookmakerContext;
  visible: boolean;
  onClose?: () => void;
}

export const BookmakerView = ({ context, visible, onClose }: Props) => {
  if (!visible) return null;

  const verdict: BookmakerVerdict = buildBookmakerVerdict(context);

  return (
    <section
      aria-label="Bookmaker View"
      style={{
        border: `1px solid ${palette.border}`,
        borderRadius: 12,
        padding: 14,
        background: palette.card,
        display: 'flex',
        flexDirection: 'column',
        gap: 8
      }}
    >
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ color: palette.textPrimary, fontSize: 16, fontWeight: 700 }}>Bookmaker View</div>
          <div style={{ color: palette.textSecondary, fontSize: 12 }}>Market Risk Commentary</div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: `1px solid ${palette.border}`,
              color: palette.textSecondary,
              borderRadius: 8,
              padding: '4px 8px',
              cursor: 'pointer'
            }}
          >
            Hide
          </button>
        )}
      </header>

      <VerdictRow label="A. Market Read" value={verdict.marketRead} />
      <VerdictRow label="B. Risk Assessment" value={verdict.riskAssessment} />

      <div
        style={{
          border: `1px solid ${palette.border}`,
          borderRadius: 10,
          padding: 10,
          background: 'rgba(255,255,255,0.02)'
        }}
      >
        <div style={{ color: palette.textSecondary, fontSize: 12, marginBottom: 6 }}>C. Trap Indicators</div>
        {verdict.trapIndicators.map((trap, idx) => (
          <div
            key={`${trap.level}-${idx}`}
            style={{
              padding: 8,
              borderRadius: 8,
              background: palette.cardElevated,
              borderLeft: `3px solid ${
                trap.level === 'high' ? palette.danger : trap.level === 'medium' ? palette.warning : palette.success
              }`,
              color: palette.textPrimary,
              fontSize: 12,
              marginBottom: idx === verdict.trapIndicators.length - 1 ? 0 : 6
            }}
          >
            <strong style={{ textTransform: 'uppercase', fontSize: 11 }}>{trap.level}</strong> — {trap.note}
          </div>
        ))}
      </div>

      <VerdictRow label="D. Timing Advice" value={verdict.timingAdvice} />
      <VerdictRow label="E. Confidence Warning" value={verdict.confidenceWarning} />

      <div style={{ fontSize: 11, color: palette.textSecondary, borderTop: `1px dashed ${palette.border}`, paddingTop: 8 }}>
        Limitations: {verdict.limitations.join(' • ')}
      </div>
    </section>
  );
};

const VerdictRow = ({ label, value }: { label: string; value: string }) => (
  <div
    style={{
      border: `1px solid ${palette.border}`,
      borderRadius: 10,
      padding: 10,
      background: 'rgba(255,255,255,0.02)',
      display: 'flex',
      flexDirection: 'column',
      gap: 4
    }}
  >
    <div style={{ color: palette.textSecondary, fontSize: 12 }}>{label}</div>
    <div style={{ color: palette.textPrimary, fontSize: 13 }}>{value}</div>
  </div>
);
