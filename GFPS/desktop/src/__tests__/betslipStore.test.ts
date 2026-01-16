import { describe, it, expect, beforeEach } from 'vitest';
import { useBetSlipStore } from '@store/betslip';

describe('bet slip store', () => {
  beforeEach(() => {
    localStorage.clear();
    useBetSlipStore.setState({
      selections: [],
      mode: 'accumulator',
      isOpen: false,
      showAnalysis: false,
      analysisData: null,
      isAnalyzing: false,
      analysisError: null,
    });
  });

  it('adds selection to slip', () => {
    const { addSelection } = useBetSlipStore.getState();
    
    addSelection({
      clientSelectionKey: 'test-1',
      homeTeam: 'Team A',
      awayTeam: 'Team B',
      league: 'League 1',
      marketType: '1x2',
      marketName: 'Match Winner',
      outcome: 'home',
      oddsBookmaker: 2.0,
    });

    const { selections } = useBetSlipStore.getState();
    expect(selections).toHaveLength(1);
    expect(selections[0].clientSelectionKey).toBe('test-1');
    expect(selections[0].homeTeam).toBe('Team A');
  });

  it('removes selection from slip', () => {
    const { addSelection, removeSelection } = useBetSlipStore.getState();
    
    addSelection({
      clientSelectionKey: 'test-1',
      homeTeam: 'Team A',
      awayTeam: 'Team B',
      league: 'League 1',
      marketType: '1x2',
      marketName: 'Match Winner',
      outcome: 'home',
      oddsBookmaker: 2.0,
    });

    removeSelection('test-1');

    const { selections } = useBetSlipStore.getState();
    expect(selections).toHaveLength(0);
  });

  it('clears all selections', () => {
    const { addSelection, clearSlip } = useBetSlipStore.getState();
    
    addSelection({
      clientSelectionKey: 'test-1',
      homeTeam: 'Team A',
      awayTeam: 'Team B',
      league: 'League 1',
      marketType: '1x2',
      marketName: 'Match Winner',
      outcome: 'home',
      oddsBookmaker: 2.0,
    });
    
    addSelection({
      clientSelectionKey: 'test-2',
      homeTeam: 'Team C',
      awayTeam: 'Team D',
      league: 'League 1',
      marketType: '1x2',
      marketName: 'Match Winner',
      outcome: 'away',
      oddsBookmaker: 2.5,
    });

    clearSlip();

    const { selections } = useBetSlipStore.getState();
    expect(selections).toHaveLength(0);
  });

  it('persists to localStorage on add', () => {
    const { addSelection } = useBetSlipStore.getState();
    
    addSelection({
      clientSelectionKey: 'test-1',
      homeTeam: 'Team A',
      awayTeam: 'Team B',
      league: 'League 1',
      marketType: '1x2',
      marketName: 'Match Winner',
      outcome: 'home',
      oddsBookmaker: 2.0,
    });

    const stored = localStorage.getItem('gfps_betslip');
    expect(stored).toBeTruthy();
    
    const parsed = JSON.parse(stored!);
    expect(parsed.selections).toHaveLength(1);
    expect(parsed.selections[0].clientSelectionKey).toBe('test-1');
  });

  it('rehydrates from localStorage', () => {
    // Manually set localStorage
    const testData = {
      selections: [
        {
          clientSelectionKey: 'test-1',
          homeTeam: 'Team A',
          awayTeam: 'Team B',
          league: 'League 1',
          marketType: '1x2',
          marketName: 'Match Winner',
          outcome: 'home',
          oddsBookmaker: 2.0,
        }
      ],
      mode: 'single',
    };
    localStorage.setItem('gfps_betslip', JSON.stringify(testData));

    const { hydrate } = useBetSlipStore.getState();
    hydrate();

    const { selections, mode } = useBetSlipStore.getState();
    expect(selections).toHaveLength(1);
    expect(selections[0].clientSelectionKey).toBe('test-1');
    expect(mode).toBe('single');
  });

  it('prevents duplicate selections', () => {
    const { addSelection } = useBetSlipStore.getState();
    
    const selection = {
      clientSelectionKey: 'test-1',
      homeTeam: 'Team A',
      awayTeam: 'Team B',
      league: 'League 1',
      marketType: '1x2',
      marketName: 'Match Winner',
      outcome: 'home',
      oddsBookmaker: 2.0,
    };
    
    addSelection(selection);
    addSelection(selection); // Try to add duplicate

    const { selections } = useBetSlipStore.getState();
    expect(selections).toHaveLength(1); // Should still be only 1
  });

  it('switches between single and accumulator modes', () => {
    const { setMode, mode: initialMode } = useBetSlipStore.getState();
    expect(initialMode).toBe('accumulator');

    setMode('single');
    expect(useBetSlipStore.getState().mode).toBe('single');

    setMode('accumulator');
    expect(useBetSlipStore.getState().mode).toBe('accumulator');
  });

  it('toggles drawer open/closed', () => {
    const { toggleOpen, isOpen: initialOpen } = useBetSlipStore.getState();
    expect(initialOpen).toBe(false);

    toggleOpen();
    expect(useBetSlipStore.getState().isOpen).toBe(true);

    toggleOpen();
    expect(useBetSlipStore.getState().isOpen).toBe(false);
  });
});
