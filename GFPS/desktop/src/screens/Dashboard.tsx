import { api } from '@api/client';
import { useQuery } from '@hooks/useQuery';
import { KpiCard } from '@components/KpiCard';
import { DataTable } from '@components/DataTable';
import { palette } from '@theme/palette';
import { ValueBet } from '@api/types';

export const Dashboard = () => {
  const fixtures = useQuery(api.fixtures, []);
  const valueBets = useQuery(api.valueBets, []);

  const activeMatches = fixtures.data?.filter((f) => f.status === 'live').length ?? 0;
  const scheduled = fixtures.data?.filter((f) => f.status === 'scheduled').length ?? 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 14 }}>
        <KpiCard label="Live Matches" value={activeMatches.toString()} subLabel="Currently trading" />
        <KpiCard label="Upcoming" value={scheduled.toString()} subLabel="Within next 24h" />
        <KpiCard label="Active Models" value="3" subLabel="production + variants" />
        <KpiCard label="EV+ signals" value={(valueBets.data?.length ?? 0).toString()} subLabel="Today" />
      </div>

      <section
        style={{
          border: `1px solid ${palette.border}`,
          borderRadius: 14,
          padding: 16,
          background: palette.cardElevated,
          display: 'flex',
          flexDirection: 'column',
          gap: 12
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ color: palette.textPrimary, fontWeight: 700, fontSize: 18 }}>Top EV+ Opportunities</div>
          <div style={{ color: palette.textSecondary, fontSize: 13 }}>Live feed from FastAPI</div>
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
            {
              header: 'EV%',
              key: 'expectedValue',
              render: (row) => `${(row.expectedValue * 100).toFixed(1)}%`
            }
          ]}
          data={valueBets.data ?? []}
        />
      </section>
    </div>
  );
};
