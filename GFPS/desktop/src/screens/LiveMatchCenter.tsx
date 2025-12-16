import { api } from '@api/client';
import { MomentumChart } from '@charts/MomentumChart';
import { ProbabilityEvolutionChart } from '@charts/ProbabilityEvolutionChart';
import { DataTable } from '@components/DataTable';
import { useQuery } from '@hooks/useQuery';
import { useLiveMatches } from '@hooks/useLiveMatches';
import { palette } from '@theme/palette';
import { ReactNode, useState } from 'react';
import { Fixture, LiveOddsRow, Prediction } from '@api/types';

export const LiveMatchCenter = () => {
  const { fixtures: liveFixtures, events } = useLiveMatches();
  const fixturesQuery = useQuery(api.fixtures, []);
  const oddsQuery = useQuery(api.liveOdds, []);
  const predictionsQuery = useQuery(api.predictions, []);
  const [selected, setSelected] = useState<Fixture | null>(null);

  const fixtures = liveFixtures.length ? liveFixtures : fixturesQuery.data ?? [];
  const liveOdds = oddsQuery.data ?? [];
  const predictions = predictionsQuery.data ?? [];

  const selectedPrediction: Prediction | undefined = predictions.find((p) => p.fixtureId === selected?.id);

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: 16, height: '100%' }}>
      <section style={{ border: `1px solid ${palette.border}`, borderRadius: 14, overflow: 'hidden' }}>
        <div style={{ padding: 14, borderBottom: `1px solid ${palette.border}`, background: 'rgba(17,24,39,0.7)' }}>
          <div style={{ color: palette.textPrimary, fontWeight: 700 }}>Live Matches</div>
          <div style={{ color: palette.textSecondary, fontSize: 13 }}>Click a row to open detail</div>
        </div>
        <div style={{ maxHeight: 'calc(100vh - 220px)', overflow: 'auto' }}>
          <DataTable<Fixture>
            columns={[
              {
                header: 'Match',
                key: 'homeTeam',
                render: (row) => (
                  <button
                    onClick={() => setSelected(row)}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      width: '100%',
                      textAlign: 'left',
                      background: 'transparent',
                      border: 'none',
                      color: palette.textPrimary,
                      cursor: 'pointer'
                    }}
                  >
                    <span style={{ fontWeight: 600 }}>
                      {row.homeTeam} vs {row.awayTeam}
                    </span>
                    <span style={{ color: palette.textSecondary, fontSize: 12 }}>{row.league}</span>
                  </button>
                )
              },
              {
                header: 'Status',
                key: 'status',
                render: (row) => <span style={{ color: '#22c55e' }}>{row.status}</span>
              },
              {
                header: 'Score',
                key: 'score',
                render: (row) =>
                  row.score ? `${row.score.home} - ${row.score.away}` : row.timer || row.startTime
              }
            ]}
            data={fixtures}
          />
        </div>
      </section>

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
        {selected ? (
          <>
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ color: palette.textPrimary, fontSize: 20, fontWeight: 700 }}>
                  {selected.homeTeam} vs {selected.awayTeam}
                </div>
                <div style={{ color: palette.textSecondary }}>
                  {selected.league} • {selected.timer || selected.startTime}
                </div>
              </div>
              <div
                style={{
                  background: 'rgba(31,154,229,0.12)',
                  padding: '8px 12px',
                  borderRadius: 10,
                  border: `1px solid ${palette.border}`,
                  color: palette.textPrimary
                }}
              >
                Live Score: {selected.score ? `${selected.score.home} - ${selected.score.away}` : 'N/A'}
              </div>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 12 }}>
              <div
                style={{
                  border: `1px solid ${palette.border}`,
                  borderRadius: 12,
                  padding: 12,
                  background: palette.card
                }}
              >
                <div style={{ color: palette.textPrimary, fontWeight: 600, marginBottom: 8 }}>Live Odds (1X2)</div>
                <DataTable<LiveOddsRow>
                  columns={[
                    { header: 'Market', key: 'market' },
                    { header: 'Home', key: 'home', render: (row) => row.home.toFixed(2) },
                    { header: 'Draw', key: 'draw', render: (row) => row.draw.toFixed(2) },
                    { header: 'Away', key: 'away', render: (row) => row.away.toFixed(2) },
                    { header: 'Source', key: 'source' }
                  ]}
                  data={liveOdds}
                />
              </div>

              <div
                style={{
                  border: `1px solid ${palette.border}`,
                  borderRadius: 12,
                  padding: 12,
                  background: palette.card
                }}
              >
                <div style={{ color: palette.textPrimary, fontWeight: 600, marginBottom: 8 }}>AI Probabilities</div>
                {selectedPrediction ? (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
                    <ProbabilityPill label="Home" value={selectedPrediction.homeWinProbability} color="#0fd7a1" />
                    <ProbabilityPill label="Draw" value={selectedPrediction.drawProbability} color="#f59e0b" />
                    <ProbabilityPill label="Away" value={selectedPrediction.awayWinProbability} color="#1f9ae5" />
                  </div>
                ) : (
                  <div style={{ color: palette.textSecondary }}>No prediction data available.</div>
                )}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <ChartCard title="Momentum" subtitle="Live dominance trajectory">
                <MomentumChart />
              </ChartCard>
              <ChartCard title="Probability Evolution" subtitle="Win/Draw/Away over time">
                <ProbabilityEvolutionChart />
              </ChartCard>
            </div>

            <div
              style={{
                border: `1px solid ${palette.border}`,
                borderRadius: 12,
                padding: 12,
                background: palette.card
              }}
            >
              <div style={{ color: palette.textPrimary, fontWeight: 600, marginBottom: 8 }}>Match Events</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {(events[selected.id] || []).map((event, idx) => (
                  <div
                    key={`${event.minute}-${idx}`}
                    style={{ display: 'flex', gap: 12, color: palette.textPrimary }}
                  >
                    <div style={{ color: palette.textSecondary, width: 40 }}>{event.minute}'</div>
                    <div>{event.description}</div>
                  </div>
                ))}
                {(events[selected.id] || []).length === 0 && (
                  <div style={{ color: palette.textSecondary }}>No live events yet.</div>
                )}
              </div>
            </div>
          </>
        ) : (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: palette.textSecondary,
              height: '100%'
            }}
          >
            Select a match to view live analytics.
          </div>
        )}
      </section>
    </div>
  );
};

const ProbabilityPill = ({ label, value, color }: { label: string; value: number; color: string }) => (
  <div
    style={{
      border: `1px solid ${palette.border}`,
      borderRadius: 12,
      padding: 12,
      background: 'rgba(255,255,255,0.02)'
    }}
  >
    <div style={{ color: palette.textSecondary, fontSize: 13 }}>{label}</div>
    <div style={{ color, fontSize: 22, fontWeight: 700 }}>{(value * 100).toFixed(1)}%</div>
  </div>
);

const ChartCard = ({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) => (
  <div
    style={{
      border: `1px solid ${palette.border}`,
      borderRadius: 12,
      padding: 12,
      background: palette.card
    }}
  >
    <div style={{ color: palette.textPrimary, fontWeight: 600 }}>{title}</div>
    <div style={{ color: palette.textSecondary, fontSize: 13, marginBottom: 8 }}>{subtitle}</div>
    {children}
  </div>
);
