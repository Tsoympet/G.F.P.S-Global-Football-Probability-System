import { useLiveMatches } from '@hooks/useLiveMatches';
import { useQuery } from '@hooks/useQuery';
import { api } from '@api/client';
import { palette } from '@theme/palette';
import { sanitizeKey } from '@utils/sanitize';
import { useState } from 'react';
import { Fixture, Prediction } from '@api/types';
import { DataTable } from '@components/DataTable';

type Verdict = 'correct' | 'incorrect' | 'uncertain';

interface FeedbackRow {
  fixtureId: string;
  userVerdict: Verdict | null;
  note: string;
}

export const AiMonitor = () => {
  const { fixtures: liveFixtures, connection, lastMessage } = useLiveMatches();
  const predictionsQuery = useQuery(api.predictions, { pollMs: 15000, cacheKey: 'monitor-predictions', ttlMs: 60000 });
  const [feedback, setFeedback] = useState<Record<string, FeedbackRow>>({});

  const fixtures = liveFixtures;
  const predictions = predictionsQuery.data ?? [];

  const setVerdict = (fixtureId: string, verdict: Verdict) => {
    const key = sanitizeKey(fixtureId);
    setFeedback((prev) => ({
      ...prev,
      [key]: { fixtureId, userVerdict: verdict, note: prev[key]?.note || '' }
    }));
  };

  const setNote = (fixtureId: string, note: string) => {
    const key = sanitizeKey(fixtureId);
    setFeedback((prev) => ({
      ...prev,
      [key]: { fixtureId, userVerdict: prev[key]?.userVerdict || null, note }
    }));
  };

  const getRowVerdict = (fixtureId: string): Verdict | null => feedback[sanitizeKey(fixtureId)]?.userVerdict ?? null;

  const getRowNote = (fixtureId: string): string => feedback[sanitizeKey(fixtureId)]?.note ?? '';

  const rows = fixtures.map((fixture) => {
    const prediction: Prediction | undefined = predictions.find((p) => p.fixtureId === fixture.id);
    return {
      ...fixture,
      prediction,
      verdict: getRowVerdict(fixture.id),
      note: getRowNote(fixture.id)
    };
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ color: palette.textPrimary, fontSize: 22, fontWeight: 800 }}>AI Monitor</div>
      <div style={{ color: palette.textSecondary, fontSize: 13 }}>
        Compare live outcomes with AI probabilities. Mark whether the prediction looks correct, incorrect, or uncertain to
        help the model improve. Feed status: {connection} {lastMessage ? `• updated ${new Date(lastMessage).toLocaleTimeString()}` : ''}
      </div>

      <div style={{ border: `1px solid ${palette.border}`, borderRadius: 12, overflow: 'hidden' }}>
        <DataTable
          columns={[
            {
              header: 'Match',
              key: 'match',
              render: (row: Fixture & { prediction?: Prediction }) => (
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span style={{ color: palette.textPrimary, fontWeight: 600 }}>
                    {row.homeTeam} vs {row.awayTeam}
                  </span>
                  <span style={{ color: palette.textSecondary, fontSize: 12 }}>{row.league}</span>
                </div>
              )
            },
            {
              header: 'AI Probabilities',
              key: 'prob',
              render: (row: Fixture & { prediction?: Prediction }) =>
                row.prediction ? (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 6 }}>
                    <Pill label="Home" value={row.prediction.homeWinProbability} color="#0fd7a1" />
                    <Pill label="Draw" value={row.prediction.drawProbability} color="#f59e0b" />
                    <Pill label="Away" value={row.prediction.awayWinProbability} color="#1f9ae5" />
                  </div>
                ) : (
                  <span style={{ color: palette.textSecondary }}>No prediction</span>
                )
            },
            {
              header: 'User verdict',
              key: 'verdict',
              render: (row: Fixture & { verdict: Verdict | null }) => (
                <div style={{ display: 'flex', gap: 8 }}>
                  {(['correct', 'incorrect', 'uncertain'] as Verdict[]).map((v) => (
                    <button
                      key={v}
                      onClick={() => setVerdict(row.id, v)}
                      style={{
                        padding: '8px 10px',
                        borderRadius: 8,
                        border: `1px solid ${palette.border}`,
                        background: row.verdict === v ? 'rgba(31,154,229,0.18)' : palette.card,
                        color: palette.textPrimary,
                        fontSize: 12,
                        cursor: 'pointer'
                      }}
                    >
                      {v}
                    </button>
                  ))}
                </div>
              )
            },
            {
              header: 'Notes (why)',
              key: 'note',
              render: (row: Fixture & { note: string }) => (
                <input
                  value={row.note}
                  onChange={(e) => setNote(row.id, e.target.value)}
                  placeholder="e.g., red card changed momentum"
                  style={{
                    width: '100%',
                    background: palette.card,
                    border: `1px solid ${palette.border}`,
                    color: palette.textPrimary,
                    padding: '8px 10px',
                    borderRadius: 8
                  }}
                />
              )
            }
          ]}
          data={rows}
        />
      </div>
    </div>
  );
};

const Pill = ({ label, value, color }: { label: string; value: number; color: string }) => (
  <div
    style={{
      border: `1px solid ${palette.border}`,
      borderRadius: 10,
      padding: '8px 10px',
      background: 'rgba(255,255,255,0.02)'
    }}
  >
    <div style={{ color: palette.textSecondary, fontSize: 11 }}>{label}</div>
    <div style={{ color, fontWeight: 700 }}>{(value * 100).toFixed(1)}%</div>
  </div>
);
