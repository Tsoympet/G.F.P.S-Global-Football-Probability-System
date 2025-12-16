import { api } from '@api/client';
import { DataTable } from '@components/DataTable';
import { useQuery } from '@hooks/useQuery';
import { palette } from '@theme/palette';
import { ValueBet } from '@api/types';

export const ValueBets = () => {
  const valueBets = useQuery(api.valueBets, []);

  return (
    <section
      style={{
        border: `1px solid ${palette.border}`,
        borderRadius: 14,
        background: palette.cardElevated,
        padding: 16,
        display: 'flex',
        flexDirection: 'column',
        gap: 12
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ color: palette.textPrimary, fontSize: 20, fontWeight: 700 }}>Value Bets (EV+)</div>
        <div style={{ color: palette.textSecondary }}>Sortable & filter-ready</div>
      </div>
      <DataTable<ValueBet>
        columns={[
          { header: 'Match', key: 'match' },
          { header: 'Market', key: 'market' },
          { header: 'Odds', key: 'odds', render: (row) => row.odds.toFixed(2) },
          {
            header: 'Model Probability',
            key: 'modelProbability',
            render: (row) => `${(row.modelProbability * 100).toFixed(1)}%`
          },
          { header: 'EV%', key: 'expectedValue', render: (row) => `${(row.expectedValue * 100).toFixed(1)}%` }
        ]}
        data={valueBets.data ?? []}
      />
    </section>
  );
};
