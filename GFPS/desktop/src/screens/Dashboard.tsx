import { api } from '@api/client';
import { useQuery } from '@hooks/useQuery';
import { KpiCard } from '@components/KpiCard';
import { DataTable } from '@components/DataTable';
import { palette } from '@theme/palette';
import { Fixture, PipelineStatus, Prediction, ValueBet } from '@api/types';
import { useSettingsStore } from '@store/settings';

export const Dashboard = () => {
  const { refreshIntervalMs, evThreshold } = useSettingsStore();
  const fixtures = useQuery(api.fixtures, { pollMs: refreshIntervalMs });
  const valueBets = useQuery(() => api.valueBets(evThreshold), { pollMs: refreshIntervalMs, deps: [evThreshold] });
  const models = useQuery(api.models, { pollMs: refreshIntervalMs * 2 });
  const pipeline = useQuery<PipelineStatus>(api.pipelineStatus, { pollMs: refreshIntervalMs * 2 });
  const predictions = useQuery<Prediction[]>(api.predictions, { pollMs: refreshIntervalMs });
  const health = useQuery(api.health, { pollMs: refreshIntervalMs * 3, staleMs: refreshIntervalMs * 6 });

  const activeMatches = fixtures.data?.filter((f) => f.status === 'live').length ?? 0;
  const scheduled = fixtures.data?.filter((f) => f.status === 'scheduled').length ?? 0;
  const activeModels = models.data?.filter((model) => model.status === 'active').length ?? 0;
  const snapshot = pipeline.data?.snapshot;
  const pipelineMeta = pipeline.data?.pipeline;
  const modelMeta = pipeline.data?.model;
  const snapshotTime = snapshot?.capturedAt ? new Date(snapshot.capturedAt).toLocaleString() : 'No snapshot yet';
  const snapshotAge =
    snapshot?.ageSec !== null && snapshot?.ageSec !== undefined
      ? `${Math.round(snapshot.ageSec)}s ago`
      : 'Awaiting refresh';
  const modelVersion = snapshot?.modelVersion ?? modelMeta?.version ?? 'n/a';
  const evDisplay = ((modelMeta?.evThreshold ?? evThreshold) * 100).toFixed(1);
  const todaysFixtures =
    fixtures.data?.filter((f) => {
      const start = new Date(f.startTime);
      const today = new Date();
      return (
        start.getUTCFullYear() === today.getUTCFullYear() &&
        start.getUTCMonth() === today.getUTCMonth() &&
        start.getUTCDate() === today.getUTCDate()
      );
    }) ?? [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {(fixtures.loading || pipeline.loading || health.loading) && (
        <div style={{ color: palette.textSecondary, fontSize: 13 }}>Syncing live data...</div>
      )}
      {(fixtures.error || pipeline.error || health.error) && (
        <div style={{ color: palette.danger }}>
          {fixtures.error || pipeline.error || health.error} — automatic retries enabled.
        </div>
      )}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 14 }}>
        <KpiCard label="Live Matches" value={activeMatches.toString()} subLabel="Currently trading" />
        <KpiCard label="Upcoming" value={scheduled.toString()} subLabel="Within next 24h" />
        <KpiCard label="Active Models" value={activeModels.toString()} subLabel="production-ready" />
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
          <div style={{ color: palette.textPrimary, fontWeight: 700, fontSize: 18 }}>Pipeline Snapshot</div>
          <div style={{ color: palette.textSecondary, fontSize: 13 }}>
            {pipelineMeta?.streamerEnabled ? 'Live streamer enabled' : 'Streamer paused'} •{' '}
            {health.data?.ok ? 'API online' : 'API degraded'}
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 12 }}>
          <PipelineMetric label="Last Snapshot" value={snapshotTime} subLabel={snapshotAge} />
          <PipelineMetric
            label="Fixtures"
            value={(snapshot?.fixtureCount ?? 0).toString()}
            subLabel={`${snapshot?.oddsCount ?? 0} odds feeds`}
          />
          <PipelineMetric
            label="Predictions"
            value={(snapshot?.predictionCount ?? 0).toString()}
            subLabel={`Model ${modelVersion}`}
          />
          <PipelineMetric
            label="Value Bets"
            value={(snapshot?.valueBetCount ?? 0).toString()}
            subLabel={`EV ≥ ${evDisplay}%`}
          />
        </div>
        <div style={{ color: palette.textSecondary, fontSize: 13, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <span>
            Alert engine: {pipelineMeta?.alertEngineEnabled ? 'active' : 'idle'} • Snapshot interval:{' '}
            {pipelineMeta?.snapshotIntervalSec ?? 0}s
          </span>
          <span>
            API health:{' '}
            {health.data?.ok
              ? 'healthy'
              : health.data
                ? `degraded (${health.data.services.database.status})`
                : 'checking...'}
          </span>
          {pipeline.stale && <span style={{ color: palette.warning }}>Data may be stale — attempting refresh</span>}
        </div>
      </section>

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
          <div style={{ color: palette.textPrimary, fontWeight: 700, fontSize: 18 }}>Today&apos;s Fixtures</div>
          {fixtures.stale && <span style={{ color: palette.warning, fontSize: 12 }}>Updating...</span>}
        </div>
        <DataTable<Fixture>
          columns={[
            { header: 'Match', key: 'homeTeam', render: (row: any) => `${row.homeTeam} vs ${row.awayTeam}` },
            { header: 'League', key: 'league' },
            { header: 'Kickoff', key: 'startTime', render: (row: any) => new Date(row.startTime).toLocaleString() },
            { header: 'Status', key: 'status' }
          ]}
          data={todaysFixtures}
        />
      </section>

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
          <div style={{ color: palette.textPrimary, fontWeight: 700, fontSize: 18 }}>Live Probabilities</div>
          {predictions.stale && <span style={{ color: palette.warning, fontSize: 12 }}>Updating feed…</span>}
        </div>
        <DataTable<Prediction>
          columns={[
            { header: 'Fixture', key: 'fixtureId' },
            {
              header: 'Home',
              key: 'homeWinProbability',
              render: (row) => `${(row.homeWinProbability * 100).toFixed(1)}%`
            },
            { header: 'Draw', key: 'drawProbability', render: (row) => `${(row.drawProbability * 100).toFixed(1)}%` },
            {
              header: 'Away',
              key: 'awayWinProbability',
              render: (row) => `${(row.awayWinProbability * 100).toFixed(1)}%`
            },
            { header: 'Model', key: 'modelVersion', render: (row) => row.modelVersion || 'live' }
          ]}
          data={(predictions.data || []).slice(0, 12)}
        />
      </section>
    </div>
  );
};

const PipelineMetric = ({ label, value, subLabel }: { label: string; value: string; subLabel: string }) => (
  <div style={{ border: `1px solid ${palette.border}`, borderRadius: 12, padding: 12, background: palette.card }}>
    <div style={{ color: palette.textSecondary, fontSize: 12 }}>{label}</div>
    <div style={{ color: palette.textPrimary, fontSize: 18, fontWeight: 700 }}>{value}</div>
    <div style={{ color: palette.textSecondary, fontSize: 12 }}>{subLabel}</div>
  </div>
);
