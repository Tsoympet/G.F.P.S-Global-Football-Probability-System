/**
 * Bet Slip Store - SIMULATION/ANALYSIS MODE ONLY
 * 
 * Manages bet slip selections for accumulator analysis.
 * No real money betting or execution capabilities.
 */

import { create } from 'zustand';

export type BetSlipSelection = {
  clientSelectionKey: string;
  fixtureId?: string;
  homeTeam: string;
  awayTeam: string;
  league: string;
  leagueId?: string;
  startTime?: string;
  marketType: string;
  marketName: string;
  line?: number;
  outcome: string;
  oddsBookmaker: number;
  oddsFair?: number;
  modelProbability?: number;
};

export type BetSlipMode = 'single' | 'accumulator';

export type AnalysisReport = {
  executiveSummary: {
    num_selections: number;
    combined_odds: number;
    combined_probability_naive: number;
    combined_probability_adjusted: number;
    expected_value_naive: number;
    expected_value_adjusted: number;
    risk_score: number;
    risk_profile: string;
    key_insight: string;
  };
  selectionBreakdown: Array<Record<string, unknown>>;
  correlationWarnings: Array<Record<string, unknown>>;
  scenarioAnalysis: Array<Record<string, unknown>>;
  professionalNotes: Array<Record<string, unknown>>;
  disclaimer: string;
};

export type BetSlipAnalysisResponse = {
  ok: boolean;
  slipId: string;
  mode: string;
  numSelections: number;
  selections: Array<Record<string, unknown>>;
  correlations: Array<Record<string, unknown>>;
  totals: {
    combinedOddsDecimal: number;
    combinedProbability: {
      naiveIndependence: number;
      correlationAdjusted: number;
    };
    expectedValueRoi: {
      naive: number;
      correlationAdjusted: number;
    };
    overroundStackingRisk: Record<string, unknown>;
    effectiveLegs?: number;
    volatilityMetrics: {
      score: number;
      profile: string;
      drivers: string[];
    };
  };
  report: AnalysisReport;
  metadata: Record<string, unknown>;
};

type BetSlipState = {
  // State
  selections: BetSlipSelection[];
  mode: BetSlipMode;
  isOpen: boolean;
  showAnalysis: boolean;
  analysisData: BetSlipAnalysisResponse | null;
  isAnalyzing: boolean;
  analysisError: string | null;
  
  // Actions
  addSelection: (selection: BetSlipSelection) => void;
  removeSelection: (key: string) => void;
  clearSlip: () => void;
  setMode: (mode: BetSlipMode) => void;
  toggleOpen: () => void;
  setShowAnalysis: (show: boolean) => void;
  setAnalysisData: (data: BetSlipAnalysisResponse | null) => void;
  setIsAnalyzing: (analyzing: boolean) => void;
  setAnalysisError: (error: string | null) => void;
  
  // Persistence
  persist: () => void;
  hydrate: () => void;
};

const STORAGE_KEY = 'gfps_betslip';

const getStoredData = (): Partial<BetSlipState> | null => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
};

const saveToStorage = (selections: BetSlipSelection[], mode: BetSlipMode): boolean => {
  try {
    const data = {
      selections,
      mode,
      savedAt: new Date().toISOString(),
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    return true;
  } catch (error) {
    console.error('Failed to save bet slip to localStorage:', error);
    return false;
  }
};

export const useBetSlipStore = create<BetSlipState>((set, get) => ({
  // Initial state
  selections: [],
  mode: 'accumulator',
  isOpen: false,
  showAnalysis: false,
  analysisData: null,
  isAnalyzing: false,
  analysisError: null,
  
  // Actions
  addSelection: (selection: BetSlipSelection) => {
    const { selections } = get();
    
    // Check for duplicate
    const exists = selections.find(s => s.clientSelectionKey === selection.clientSelectionKey);
    if (exists) {
      console.warn('Selection already in slip:', selection.clientSelectionKey);
      return;
    }
    
    const newSelections = [...selections, selection];
    set({ selections: newSelections, showAnalysis: false, analysisData: null });
    saveToStorage(newSelections, get().mode);
  },
  
  removeSelection: (key: string) => {
    const { selections } = get();
    const newSelections = selections.filter(s => s.clientSelectionKey !== key);
    set({ selections: newSelections, showAnalysis: false, analysisData: null });
    saveToStorage(newSelections, get().mode);
  },
  
  clearSlip: () => {
    set({ 
      selections: [], 
      showAnalysis: false, 
      analysisData: null,
      analysisError: null 
    });
    saveToStorage([], get().mode);
  },
  
  setMode: (mode: BetSlipMode) => {
    set({ mode });
    saveToStorage(get().selections, mode);
  },
  
  toggleOpen: () => {
    set(state => ({ isOpen: !state.isOpen }));
  },
  
  setShowAnalysis: (show: boolean) => {
    set({ showAnalysis: show });
  },
  
  setAnalysisData: (data: BetSlipAnalysisResponse | null) => {
    set({ analysisData: data });
  },
  
  setIsAnalyzing: (analyzing: boolean) => {
    set({ isAnalyzing: analyzing });
  },
  
  setAnalysisError: (error: string | null) => {
    set({ analysisError: error });
  },
  
  // Persistence
  persist: () => {
    const { selections, mode } = get();
    saveToStorage(selections, mode);
  },
  
  hydrate: () => {
    const stored = getStoredData();
    if (stored && stored.selections) {
      set({
        selections: stored.selections,
        mode: stored.mode || 'accumulator',
      });
    }
  },
}));
