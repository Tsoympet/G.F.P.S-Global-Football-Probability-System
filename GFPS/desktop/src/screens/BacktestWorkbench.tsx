import React, { useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
} from 'chart.js';
import { api } from '@api/client';
import { BacktestMetrics, BacktestRun, BacktestRequestPayload } from '@api/types';
import { useQuery } from '@hooks/useQuery';
import { KpiCard } from '@components/KpiCard';
import { DataTable } from '@components/DataTable';
import { palette } from '@theme/palette';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export const BacktestWorkbench = () => {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [minEv, setMinEv] = useState(0.02);
  const [minConfidence, setMinConfidence] = useState(0.5);
  const [maxPerDay, setMaxPerDay] = useState(5);
  const [correlation, setCorrelation] = useState(0.5);
  const [stake, setStake] = useState(1);
  const [result, setResult] = useState<BacktestMetrics | null>(null);
  const [latestRunId, setLatestRunId] = useState<number | null>(null);
  const [running, setRunning] = useState(false);
  const runs = useQuery<BacktestRun[]>(api.backtests, { pollMs: 120000, cacheKey: 'backtests' });

  const runBacktest = async () => {
    setRunning(true);
    try {
      const payload: BacktestRequestPayload = {
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        seed: 7,
        rules: {
          markets: ['1x2'],
          min_ev: Number(minEv),
          min_confidence: Number(minConfidence),
          max_per_day: Number(maxPerDay),
          correlation_threshold: Number(correlation),
          stake_model: 'flat',
          base_stake: Number(stake),
          kelly_fraction: 0.25,
          use_fair_odds_if_missing: true,
        },
      };
      const response = await api.runBacktest(payload);
      setResult(response.metrics);
      setLatestRunId(response.runId);
      await runs.refetch();
    } finally {
      setRunning(false);
    }
  };

  const exportReport = () => {
    if (!result) return;
    const payload = JSON.stringify({ runId: latestRunId, metrics: result }, null, 2);
    const blob = new Blob([payload], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `backtest-${latestRunId || 'latest'}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const drawdown = result?.drawdownCurve || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 12 }}>
        <KpiCard label="ROI" value={`${((result?.roi ?? 0) * 100).toFixed(2)}%`} subLabel="Backtest" />
        <KpiCard label="Hit Rate" value={`${((result?.hitRate ?? 0) * 100).toFixed(1)}%`} subLabel="Settled picks" />
        <KpiCard label="Max Drawdown" value={(result?.maxDrawdown ?? 0).toFixed(2)} subLabel="Units" />
        <KpiCard label="Sample" value={(result?.sampleSize ?? 0).toString()} subLabel="Selections" />
      </div>

      <section
        style={{
          border: `1px solid ${palette.border}`,
          borderRadius: 12,
          padding: 14,
          background: palette.cardElevated,
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 12,
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ color: palette.textPrimary, fontWeight: 700 }}>Configure rules</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 8 }}>
            <input value={startDate} onChange={(e) => setStartDate(e.target.value)} placeholder="Start date (ISO)" style={inputStyle} />
            <input value={endDate} onChange={(e) => setEndDate(e.target.value)} placeholder="End date (ISO)" style={inputStyle} />
            <input type="number" step="0.01" value={minEv} onChange={(e) => setMinEv(Number(e.target.value))} placeholder="Min EV" style={inputStyle} />
            <input
              type="number"
              step="0.05"
              value={minConfidence}
              onChange={(e) => setMinConfidence(Number(e.target.value))}
              placeholder="Confidence min"
              style={inputStyle}
            />
            <input type="number" value={maxPerDay} onChange={(e) => setMaxPerDay(Number(e.target.value))} placeholder="Max per day" style={inputStyle} />
            <input
              type="number"
              step="0.1"
              value={correlation}
              onChange={(e) => setCorrelation(Number(e.target.value))}
              placeholder="Correlation threshold"
              style={inputStyle}
            />
            <input type="number" step="0.25" value={stake} onChange={(e) => setStake(Number(e.target.value))} placeholder="Flat stake" style={inputStyle} />
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <button onClick={runBacktest} disabled={running} style={buttonStyle}>
              {running ? 'Running…' : 'Run backtest'}
            </button>
            <button onClick={exportReport} disabled={!result} style={buttonAlt}>
              Export JSON
            </button>
          </div>
          {result?.honesty?.warnings?.length ? (
            <div style={{ color: palette.warning, fontSize: 12 }}>
              Honesty panel: {result.honesty.warnings.join(' • ')}
            </div>
          ) : null}
        </div>
        <div>
          <div style={{ color: palette.textPrimary, fontWeight: 700, marginBottom: 8 }}>Drawdown curve</div>
          <Line
            data={{
              labels: drawdown.map((p) => p.idx),
              datasets: [
                {
                  label: 'Equity drawdown',
                  data: drawdown.map((p) => p.drawdown),
                  borderColor: '#f59e0b',
                  backgroundColor: 'rgba(245,158,11,0.14)',
                },
              ],
            }}
            options={{
              plugins: { legend: { labels: { color: '#e5e7eb' } } },
              scales: {
                x: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
              },
            }}
          />
        </div>
      </section>

      <section
        style={{
          border: `1px solid ${palette.border}`,
          borderRadius: 12,
          padding: 14,
          background: palette.cardElevated,
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 12,
        }}
      >
        <div>
          <div style={{ color: palette.textPrimary, fontWeight: 700, marginBottom: 6 }}>Sensitivity (EV sweep)</div>
          <DataTable<{ evThreshold: number; roi: number }>
            columns={[
              { header: 'EV Threshold', key: 'evThreshold', render: (row) => `${(row.evThreshold * 100).toFixed(1)}%` },
              { header: 'ROI', key: 'roi', render: (row) => `${(row.roi * 100).toFixed(2)}%` },
            ]}
            data={result?.sensitivity || []}
          />
        </div>
        <div>
          <div style={{ color: palette.textPrimary, fontWeight: 700, marginBottom: 6 }}>Correlation impact</div>
          <div style={{ color: palette.textSecondary, fontSize: 13 }}>
            With filter: {((result?.correlationImpact?.withFilter ?? 0) * 100).toFixed(2)}% ROI • Without filter:{' '}
            {((result?.correlationImpact?.withoutFilter ?? 0) * 100).toFixed(2)}% ROI
          </div>
        </div>
      </section>

      <section
        style={{
          border: `1px solid ${palette.border}`,
          borderRadius: 12,
          padding: 14,
          background: palette.cardElevated,
        }}
      >
        <div style={{ color: palette.textPrimary, fontWeight: 700, marginBottom: 8 }}>Previous runs</div>
        <DataTable<BacktestRun>
          columns={[
            { header: 'Run ID', key: 'id' },
            { header: 'Status', key: 'status' },
            { header: 'ROI', key: 'metrics', render: (row) => `${(((row.metrics)?.roi ?? 0) * 100).toFixed(2)}%` },
            { header: 'Sample', key: 'metrics', render: (row) => row.metrics?.sampleSize ?? 0 },
            { header: 'Completed', key: 'completedAt', render: (row) => row.completedAt ?? '-' },
          ]}
          data={runs.data || []}
        />
      </section>
    </div>
  );
};

const inputStyle: React.CSSProperties = {
  padding: 10,
  borderRadius: 8,
  border: `1px solid ${palette.border}`,
  background: palette.card,
  color: palette.textPrimary,
};

const buttonStyle: React.CSSProperties = {
  background: palette.primary,
  color: palette.textPrimary,
  border: 'none',
  padding: '10px 12px',
  borderRadius: 8,
  cursor: 'pointer',
  fontWeight: 700,
};

const buttonAlt: React.CSSProperties = {
  background: palette.card,
  color: palette.textPrimary,
  border: `1px solid ${palette.border}`,
  padding: '10px 12px',
  borderRadius: 8,
  cursor: 'pointer',
};
