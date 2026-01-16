import { api } from '@api/client';
import { DataTable } from '@components/DataTable';
import { useQuery } from '@hooks/useQuery';
import { palette } from '@theme/palette';
import { ValueBet } from '@api/types';
import { useSettingsStore } from '@store/settings';
import { useBetSlipStore } from '@store/betslip';
import { useMemo, useState } from 'react';
import { escapeCsvField } from '@app/csv';

export const ValueBets = () => {
  const { evThreshold, setEvThreshold, refreshIntervalMs } = useSettingsStore();
  const { addSelection, toggleOpen } = useBetSlipStore();
  const valueBets = useQuery(() => api.valueBets(evThreshold), {
    pollMs: refreshIntervalMs,
    deps: [evThreshold],
    cacheKey: `value-${evThreshold}`,
    ttlMs: refreshIntervalMs * 6
  });
  const fixtures = useQuery(api.fixtures, { pollMs: refreshIntervalMs * 2, cacheKey: 'fixtures' });
  const [leagueFilter, setLeagueFilter] = useState<string>('all');
  const [marketFilter, setMarketFilter] = useState<string>('all');
  const [sortKey, setSortKey] = useState<'ev' | 'kickoff'>('ev');
  const [minProb, setMinProb] = useState<number>(0);

  const fixtureLookup = useMemo(() => {
    const map: Record<string, { league?: string; startTime?: string; fixtureId?: string }> = {};
    (fixtures.data || []).forEach((f) => {
      map[`${f.homeTeam} vs ${f.awayTeam}`] = { league: f.league, startTime: f.startTime, fixtureId: f.id };
    });
    return map;
  }, [fixtures.data]);

  const enriched = useMemo(() => {
    return (valueBets.data || []).map((row) => {
      const fixture = fixtureLookup[row.match] || {};
      return { ...row, league: row.league ?? fixture.league, startTime: row.startTime ?? fixture.startTime, fixtureId: row.fixtureId ?? fixture.fixtureId };
    });
  }, [fixtureLookup, valueBets.data]);

  const leagues = Array.from(new Set(enriched.map((v) => v.league).filter(Boolean))) as string[];
  const markets = Array.from(new Set(enriched.map((v) => v.market)));

  const filtered = enriched.filter((row) => {
    const leagueOk = leagueFilter === 'all' || row.league === leagueFilter;
    const marketOk = marketFilter === 'all' || row.market === marketFilter;
    const probOk = (row.modelProbability ?? 0) >= minProb;
    return leagueOk && marketOk && probOk;
  });

  const sorted = filtered.sort((a, b) => {
    if (sortKey === 'kickoff') {
      const timeA = a.startTime ? new Date(a.startTime).getTime() : Number.MAX_SAFE_INTEGER;
      const timeB = b.startTime ? new Date(b.startTime).getTime() : Number.MAX_SAFE_INTEGER;
      return timeA - timeB;
    }
    return (b.expectedValue ?? 0) - (a.expectedValue ?? 0);
  });

  const handleExport = () => {
    const rows = sorted.map((row) => ({
      match: row.match,
      market: row.market,
      odds: row.odds,
      modelProbability: row.modelProbability,
      expectedValue: row.expectedValue,
      league: row.league,
      startTime: row.startTime
    }));
    const csv = [
      'match,market,odds,modelProbability,expectedValue,league,startTime',
      ...rows.map((r) =>
        [
          escapeCsvField(r.match),
          escapeCsvField(r.market),
          escapeCsvField(r.odds.toFixed(2)),
          escapeCsvField(((r.modelProbability ?? 0) * 100).toFixed(2)),
          escapeCsvField(((r.expectedValue ?? 0) * 100).toFixed(2)),
          escapeCsvField(r.league ?? ''),
          escapeCsvField(r.startTime ?? '')
        ].join(',')
      )
    ].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'gfps-value-bets.csv';
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleAddToBetSlip = (row: ValueBet) => {
    const fixture = fixtureLookup[row.match];
    const [homeTeam, awayTeam] = row.match.split(' vs ');
    
    addSelection({
      clientSelectionKey: `vb-${row.market}-${row.match}-${Date.now()}`,
      fixtureId: fixture?.fixtureId,
      homeTeam: homeTeam || 'Home',
      awayTeam: awayTeam || 'Away',
      league: row.league || 'Unknown',
      leagueId: row.league,
      startTime: fixture?.startTime,
      marketType: row.market.includes('Winner') ? '1x2' : 'other',
      marketName: row.market,
      outcome: row.market.split(' - ').pop() || '',
      oddsBookmaker: row.odds,
      modelProbability: row.modelProbability,
    });
    toggleOpen();
  };

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
        <div style={{ color: palette.textSecondary }}>
          EV threshold {Math.round(evThreshold * 100)}% • {valueBets.stale ? 'refreshing…' : 'live'}
        </div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 10 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <label style={{ color: palette.textSecondary, fontSize: 12 }}>EV threshold (%)</label>
          <input
            type="range"
            min={1}
            max={20}
            value={Math.round(evThreshold * 100)}
            onChange={(e) => setEvThreshold(Number(e.target.value) / 100)}
          />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <label style={{ color: palette.textSecondary, fontSize: 12 }}>League</label>
          <select
            value={leagueFilter}
            onChange={(e) => setLeagueFilter(e.target.value)}
            style={{
              background: palette.card,
              border: `1px solid ${palette.border}`,
              color: palette.textPrimary,
              padding: '10px 12px',
              borderRadius: 8
            }}
          >
            <option value="all">All leagues</option>
            {leagues.map((league) => (
              <option key={league} value={league || 'unknown'}>
                {league}
              </option>
            ))}
          </select>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <label style={{ color: palette.textSecondary, fontSize: 12 }}>Market</label>
          <select
            value={marketFilter}
            onChange={(e) => setMarketFilter(e.target.value)}
            style={{
              background: palette.card,
              border: `1px solid ${palette.border}`,
              color: palette.textPrimary,
              padding: '10px 12px',
              borderRadius: 8
            }}
          >
            <option value="all">All markets</option>
            {markets.map((market) => (
              <option key={market} value={market}>
                {market}
              </option>
            ))}
          </select>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <label style={{ color: palette.textSecondary, fontSize: 12 }}>Sort</label>
          <select
            value={sortKey}
            onChange={(e) => setSortKey(e.target.value as 'ev' | 'kickoff')}
            style={{
              background: palette.card,
              border: `1px solid ${palette.border}`,
              color: palette.textPrimary,
              padding: '10px 12px',
              borderRadius: 8
            }}
          >
            <option value="ev">EV (high → low)</option>
            <option value="kickoff">Kickoff time</option>
          </select>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <label style={{ color: palette.textSecondary, fontSize: 12 }}>Min model probability</label>
          <input
            type="number"
            min={0}
            max={1}
            step={0.01}
            value={minProb}
            onChange={(e) => setMinProb(Number(e.target.value))}
            style={{
              background: palette.card,
              border: `1px solid ${palette.border}`,
              color: palette.textPrimary,
              padding: '10px 12px',
              borderRadius: 8
            }}
          />
        </div>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: palette.textSecondary }}>
        {(valueBets.loading || fixtures.loading) && <div>Loading EV feed…</div>}
        {valueBets.error && <div style={{ color: palette.danger }}>{valueBets.error}</div>}
        <button
          onClick={handleExport}
          style={{
            background: 'linear-gradient(90deg, #1f9ae5, #0fd7a1)',
            color: '#0b0f1a',
            border: 'none',
            padding: '8px 12px',
            borderRadius: 10,
            fontWeight: 700,
            cursor: 'pointer'
          }}
        >
          Export CSV
        </button>
      </div>
      <DataTable<ValueBet>
        columns={[
          { header: 'Match', key: 'match' },
          { header: 'Market', key: 'market' },
          { header: 'Odds', key: 'odds', render: (row) => row.odds.toFixed(2) },
          {
            header: 'Model Probability',
            key: 'modelProbability',
            render: (row) => `${((row.modelProbability ?? 0) * 100).toFixed(1)}%`
          },
          {
            header: 'EV%',
            key: 'expectedValue',
            render: (row) => `${((row.expectedValue ?? 0) * 100).toFixed(1)}%`
          },
          {
            header: 'Kickoff',
            key: 'startTime',
            render: (row) => (row.startTime ? new Date(row.startTime).toLocaleString() : 'n/a')
          },
          { header: 'League', key: 'league', render: (row) => row.league || 'n/a' },
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
                  padding: '6px 12px',
                  borderRadius: 6,
                  cursor: 'pointer',
                  fontSize: 12,
                  fontWeight: 600,
                }}
              >
                + Add to Bet Slip
              </button>
            )
          }
        ]}
        data={sorted}
      />
    </section>
  );
};
