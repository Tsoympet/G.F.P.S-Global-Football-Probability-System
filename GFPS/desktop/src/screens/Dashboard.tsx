import { api } from '@api/client';
import { useQuery } from '@hooks/useQuery';
import { KpiCard } from '@components/KpiCard';
import { DataTable } from '@components/DataTable';
import { BackendSetupBanner } from '@components/BackendSetupBanner';
import { palette } from '@theme/palette';
import { Fixture, PipelineStatus, Prediction, ValueBet } from '@api/types';
import { useSettingsStore } from '@store/settings';
import { useBetSlipStore } from '@store/betslip';
import { useEffect, useState } from 'react';
import { ProbabilityEvolutionChart } from '@charts/ProbabilityEvolutionChart';

const MAX_HISTORY_POINTS = 20;
const PERCENTAGE_PRECISION = 2;

export const Dashboard = () => {
  const { refreshIntervalMs, evThreshold } = useSettingsStore();
  const { addSelection, toggleOpen } = useBetSlipStore();
  const fixtures = useQuery(api.fixtures, { pollMs: refreshIntervalMs, cacheKey: 'fixtures' });
  const valueBets = useQuery(() => api.valueBets(evThreshold), {
    pollMs: refreshIntervalMs,
    deps: [evThreshold],
    cacheKey: `value-${evThreshold}`
  });
  const models = useQuery(api.models, { pollMs: refreshIntervalMs * 2, cacheKey: 'models' });
  const pipeline = useQuery<PipelineStatus>(api.pipelineStatus, {
    pollMs: refreshIntervalMs * 2,
    cacheKey: 'pipeline'
  });
  const predictions = useQuery<Prediction[]>(api.predictions, {
    pollMs: refreshIntervalMs,
    cacheKey: 'predictions'
  });
  const health = useQuery(api.health, { pollMs: refreshIntervalMs * 3, staleMs: refreshIntervalMs * 6, cacheKey: 'health' });
  const [probabilityHistory, setProbabilityHistory] = useState<{ label: string; home: number; draw: number; away: number }[]>([]);

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

  useEffect(() => {
    if (!predictions.data?.length || !predictions.lastUpdated) return;
    const totals = predictions.data.reduce(
      (acc, p) => ({
        home: acc.home + p.homeWinProbability,
        draw: acc.draw + p.drawProbability,
        away: acc.away + p.awayWinProbability
      }),
      { home: 0, draw: 0, away: 0 }
    );
    const count = predictions.data.length || 1;
    const home = totals.home / count;
    const draw = totals.draw / count;
    const away = totals.away / count;
    const label = new Date(predictions.lastUpdated || Date.now()).toLocaleTimeString();
    const format = (value: number) => +(value * 100).toFixed(PERCENTAGE_PRECISION);
    const newPoint = { label, home: format(home), draw: format(draw), away: format(away) };
    
    // Use queueMicrotask to defer state update and avoid cascading renders
    queueMicrotask(() => {
      setProbabilityHistory((prev) => {
        if (prev.length && prev[prev.length - 1].label === label) return prev;
        return [...prev.slice(-MAX_HISTORY_POINTS), newPoint];
      });
    });
  }, [predictions.data, predictions.lastUpdated]);

  const xgRows =
    predictions.data
      ?.filter((p) => p.expectedGoalsHome !== undefined || p.expectedGoalsAway !== undefined)
      .slice(0, 8)
      .map((p) => ({
        fixtureId: p.fixtureId,
        homeTeam: p.homeTeam ?? 'Home',
        awayTeam: p.awayTeam ?? 'Away',
        xg: `${(p.expectedGoalsHome ?? 0).toFixed(2)} - ${(p.expectedGoalsAway ?? 0).toFixed(2)}`
      })) || [];

  const handleAddToBetSlip = (row: ValueBet) => {
    const [homeTeam, awayTeam] = row.match.split(' vs ');
    
    addSelection({
      clientSelectionKey: `dash-${row.market}-${row.match}-${Date.now()}`,
      homeTeam: homeTeam || 'Home',
      awayTeam: awayTeam || 'Away',
      league: 'Unknown',
      marketType: row.market.includes('Winner') ? '1x2' : 'other',
      marketName: row.market,
      outcome: row.market.split(' - ').pop() || '',
      oddsBookmaker: row.odds,
      modelProbability: row.modelProbability,
    });
    toggleOpen();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {(fixtures.loading || pipeline.loading || health.loading) && (
        <div style={{ color: palette.textSecondary, fontSize: 13 }}>Syncing live data...</div>
      )}
      {(fixtures.error || pipeline.error || health.error) && (
        <BackendSetupBanner error={fixtures.error || pipeline.error || health.error || ''} />
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
            { header: 'Match', key: 'homeTeam', render: (row: Fixture) => `${row.homeTeam} vs ${row.awayTeam}` },
            { header: 'League', key: 'league' },
            { header: 'Kickoff', key: 'startTime', render: (row: Fixture) => new Date(row.startTime).toLocaleString() },
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
          display: 'grid',
          gridTemplateColumns: '1.2fr 0.8fr',
          gap: 12
        }}
      >
        <div>
          <div style={{ color: palette.textPrimary, fontWeight: 700, fontSize: 18, marginBottom: 8 }}>
            Probability Curve (avg)
          </div>
          <ProbabilityEvolutionChart
            labels={probabilityHistory.map((p) => p.label)}
            home={probabilityHistory.map((p) => p.home)}
            draw={probabilityHistory.map((p) => p.draw)}
            away={probabilityHistory.map((p) => p.away)}
          />
        </div>
        <div>
          <div style={{ color: palette.textPrimary, fontWeight: 700, fontSize: 18, marginBottom: 8 }}>xG Snapshot</div>
          <DataTable<{ fixtureId: string; homeTeam: string; awayTeam: string; xg: string }>
            columns={[
              { header: 'Fixture', key: 'fixtureId', render: (row) => `${row.homeTeam} vs ${row.awayTeam}` },
              { header: 'xG', key: 'xg' }
            ]}
            data={xgRows}
          />
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
            },
            {
              header: 'Action',
              key: 'action',
              render: (row) => (
                <button
                  onClick={() => handleAddToBetSlip(row)}
                  style={{
                    background: palette.primary,
                    color: palette.textPrimary,
                    border: 'none',
                    padding: '4px 8px',
                    borderRadius: 4,
                    cursor: 'pointer',
                    fontSize: 11,
                    fontWeight: 600,
                  }}
                >
                  + Add
                </button>
              )
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
