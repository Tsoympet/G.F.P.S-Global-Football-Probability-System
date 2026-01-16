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
import { BetJournalEntry, PerformanceKpis } from '@api/types';
import { useQuery } from '@hooks/useQuery';
import { KpiCard } from '@components/KpiCard';
import { DataTable } from '@components/DataTable';
import { palette } from '@theme/palette';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

const defaultForm = {
  fixture_id: '',
  market: '1x2',
  side: 'home',
  model_probability: 0.55,
  bookmaker_odds: 2,
  stake: 1,
  confidence: 0.5,
  correlation_risk: 0.1
};

export const Performance = () => {
  const kpis = useQuery<PerformanceKpis>(api.performanceKpis, { pollMs: 60000, cacheKey: 'kpis' });
  const journal = useQuery<BetJournalEntry[]>(api.betJournal, { pollMs: 60000, cacheKey: 'journal' });
  const [form, setForm] = useState(defaultForm);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  const handleChange = (key: string, value: any) => setForm((prev) => ({ ...prev, [key]: value }));

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    try {
      await api.recordBetJournal({
        fixture_id: form.fixture_id || 'manual',
        market: form.market,
        side: form.side,
        model_probability: Number(form.model_probability),
        bookmaker_odds: Number(form.bookmaker_odds),
        ev: Number(form.model_probability) * Number(form.bookmaker_odds) - 1,
        confidence: Number(form.confidence),
        correlation_risk: Number(form.correlation_risk),
        stake: Number(form.stake)
      });
      await journal.refetch();
      await kpis.refetch();
      setMessage('Saved to journal');
      setForm(defaultForm);
    } catch (error: any) {
      setMessage(error?.message || 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const drawdownData = kpis.data?.drawdownCurve || [];
  const roiData = kpis.data?.roiCurve || [];

  const exportJson = () => {
    const payload = JSON.stringify({ kpis: kpis.data, journal: journal.data }, null, 2);
    const blob = new Blob([payload], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'performance.json';
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, minmax(0, 1fr))', gap: 12 }}>
        <KpiCard label="ROI" value={`${((kpis.data?.roi ?? 0) * 100).toFixed(2)}%`} subLabel="Realized" />
        <KpiCard label="Hit Rate" value={`${((kpis.data?.hitRate ?? 0) * 100).toFixed(1)}%`} subLabel="Settled" />
        <KpiCard label="Drawdown" value={`${(kpis.data?.maxDrawdown ?? 0).toFixed(2)}`} subLabel="Max" />
        <KpiCard label="Open Bets" value={(kpis.data?.pending ?? 0).toString()} subLabel="Pending settlement" />
        <KpiCard label="Total Logged" value={(kpis.data?.totalBets ?? 0).toString()} subLabel="Journal entries" />
      </div>

      <section style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: 12 }}>
        <ChartCard title="ROI over time">
          <Line
            data={{
              labels: roiData.map((p) => p.timestamp),
              datasets: [
                {
                  label: 'ROI',
                  data: roiData.map((p) => (p.roi ?? 0) * 100),
                  borderColor: '#1f9ae5',
                  backgroundColor: 'rgba(31,154,229,0.14)',
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
        </ChartCard>
        <ChartCard title="Drawdown">
          <Line
            data={{
              labels: drawdownData.map((p) => p.idx),
              datasets: [
                {
                  label: 'Drawdown',
                  data: drawdownData.map((p) => p.drawdown),
                  borderColor: '#f59e0b',
                  backgroundColor: 'rgba(245,158,11,0.18)',
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
        </ChartCard>
      </section>

      <section
        style={{
          border: `1px solid ${palette.border}`,
          borderRadius: 12,
          padding: 14,
          background: palette.cardElevated,
          display: 'grid',
          gridTemplateColumns: '1fr 1fr 1fr',
          gap: 12,
        }}
      >
        <Breakdown title="By League" rows={kpis.data?.byLeague || []} />
        <Breakdown title="By Market" rows={kpis.data?.byMarket || []} />
        <Breakdown title="7/30/90d Windows" rows={Object.entries(kpis.data?.windows || {}).map(([label, row]) => ({ label, ...row }))} />
      </section>

      <section
        style={{
          border: `1px solid ${palette.border}`,
          borderRadius: 12,
          padding: 14,
          background: palette.cardElevated,
          display: 'flex',
          gap: 16,
          alignItems: 'flex-start',
        }}
      >
        <form onSubmit={handleSave} style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 10, flex: 1 }}>
          <h3 style={{ gridColumn: '1 / -1', margin: 0, color: palette.textPrimary }}>Record simulated stake</h3>
          <input value={form.fixture_id} onChange={(e) => handleChange('fixture_id', e.target.value)} placeholder="Fixture ID" required style={inputStyle} />
          <input value={form.market} onChange={(e) => handleChange('market', e.target.value)} placeholder="Market" style={inputStyle} />
          <select value={form.side} onChange={(e) => handleChange('side', e.target.value)} style={inputStyle}>
            <option value="home">Home</option>
            <option value="draw">Draw</option>
            <option value="away">Away</option>
          </select>
          <input
            type="number"
            step="0.01"
            value={form.model_probability}
            onChange={(e) => handleChange('model_probability', e.target.value)}
            placeholder="Model probability"
            style={inputStyle}
          />
          <input
            type="number"
            step="0.01"
            value={form.bookmaker_odds}
            onChange={(e) => handleChange('bookmaker_odds', e.target.value)}
            placeholder="Bookmaker odds"
            style={inputStyle}
          />
          <input
            type="number"
            step="0.1"
            value={form.stake}
            onChange={(e) => handleChange('stake', e.target.value)}
            placeholder="Stake"
            style={inputStyle}
          />
          <input
            type="number"
            step="0.05"
            value={form.confidence}
            onChange={(e) => handleChange('confidence', e.target.value)}
            placeholder="Confidence"
            style={inputStyle}
          />
          <input
            type="number"
            step="0.05"
            value={form.correlation_risk}
            onChange={(e) => handleChange('correlation_risk', e.target.value)}
            placeholder="Correlation risk"
            style={inputStyle}
          />
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', gridColumn: '1 / -1' }}>
            <button type="submit" disabled={saving} style={buttonStyle}>
              {saving ? 'Saving...' : 'Log simulated bet'}
            </button>
            <button
              type="button"
              onClick={async () => {
                try {
                  await api.reconcileJournal();
                  await kpis.refetch();
                  setMessage('Reconciled pending entries');
                } catch (error: any) {
                  setMessage(error?.message || 'Reconcile failed');
                }
              }}
              style={buttonAlt}
            >
              Reconcile results
            </button>
            <button type="button" onClick={exportJson} style={buttonAlt}>
              Export JSON
            </button>
            {message && <span style={{ color: palette.textSecondary, fontSize: 12 }}>{message}</span>}
          </div>
        </form>
        <div style={{ flex: 1 }}>
          <div style={{ color: palette.textPrimary, fontWeight: 700, marginBottom: 8 }}>Recent Journal Entries</div>
          <DataTable<BetJournalEntry>
            columns={[
              { header: 'Fixture', key: 'fixture_ids', render: (row) => row.fixture_ids?.join(', ') || '-' },
              { header: 'Market', key: 'market' },
              { header: 'Side', key: 'side' },
              { header: 'EV', key: 'ev', render: (row) => `${(row.ev * 100).toFixed(1)}%` },
              { header: 'Odds', key: 'bookmaker_odds', render: (row) => (row.bookmaker_odds ?? 0).toFixed(2) },
              { header: 'Result', key: 'result', render: (row) => row.result || row.status },
              { header: 'ROI', key: 'realized_roi', render: (row) => `${((row.realized_roi ?? 0) * 100).toFixed(1)}%` },
            ]}
            data={(journal.data || []).slice(0, 12)}
          />
        </div>
      </section>
    </div>
  );
};

const ChartCard = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <div style={{ border: `1px solid ${palette.border}`, borderRadius: 12, padding: 14, background: palette.cardElevated }}>
    <div style={{ color: palette.textPrimary, fontWeight: 700, marginBottom: 6 }}>{title}</div>
    {children}
  </div>
);

const Breakdown = ({ title, rows }: { title: string; rows: any[] }) => (
  <div>
    <div style={{ color: palette.textPrimary, fontWeight: 700, marginBottom: 6 }}>{title}</div>
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {rows.map((row) => (
        <div key={row.label} style={{ display: 'flex', justifyContent: 'space-between', color: palette.textSecondary, fontSize: 13 }}>
          <span>{row.label}</span>
          <span>
            ROI {(row.roi * 100).toFixed(1)}% • Hit {(row.hitRate * 100).toFixed(0)}% • {row.count} bets
          </span>
        </div>
      ))}
      {!rows.length && <div style={{ color: palette.textSecondary, fontSize: 12 }}>No data yet</div>}
    </div>
  </div>
);

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
