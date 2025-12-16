import { palette } from '@theme/palette';

interface Props {
  label: string;
  value: string;
  subLabel?: string;
}

export const KpiCard = ({ label, value, subLabel }: Props) => {
  return (
    <div
      style={{
        background: `linear-gradient(160deg, rgba(31,154,229,0.15), rgba(15,215,161,0.12))`,
        border: `1px solid ${palette.border}`,
        borderRadius: 14,
        padding: 16,
        minWidth: 180,
        boxShadow: '0 10px 40px rgba(0,0,0,0.35)'
      }}
    >
      <div style={{ color: palette.textSecondary, fontSize: 13, marginBottom: 8 }}>{label}</div>
      <div style={{ color: palette.textPrimary, fontSize: 28, fontWeight: 700 }}>{value}</div>
      {subLabel && <div style={{ color: palette.textSecondary, marginTop: 6 }}>{subLabel}</div>}
    </div>
  );
};
