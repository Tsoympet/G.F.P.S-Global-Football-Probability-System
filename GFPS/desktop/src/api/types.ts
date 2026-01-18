export interface Fixture {
  id: string;
  homeTeam: string;
  awayTeam: string;
  league: string;
  leagueId?: string | null;
  startTime: string;
  status: 'scheduled' | 'live' | 'finished';
  timer?: string;
  score?: {
    home: number;
    away: number;
  };
  [key: string]: unknown;
}

export interface LiveOddsRow {
  fixtureId?: string;
  market: string;
  home: number;
  draw: number;
  away: number;
  source?: string;
  startTime?: string;
  [key: string]: unknown;
}

export interface AdditionalMarketLine {
  fixtureId: string;
  label: string;
  type: 'total' | 'handicap';
  line: string;
  over?: number;
  under?: number;
  home?: number;
  away?: number;
  source?: string;
  [key: string]: unknown;
}

export interface LiveOddsPayload {
  outrights: LiveOddsRow[];
  markets: Record<string, AdditionalMarketLine[]>;
}

export interface ProbabilitySet {
  home: number;
  draw: number;
  away: number;
}

export interface Prediction {
  fixtureId: string;
  homeWinProbability: number;
  drawProbability: number;
  awayWinProbability: number;
  homeTeam?: string;
  awayTeam?: string;
  league?: string;
  startTime?: string;
  expectedGoalsHome?: number;
  expectedGoalsAway?: number;
  pricedProbabilities?: ProbabilitySet;
  finalOdds?: ProbabilitySet;
  modelVersion?: string;
  confidence?: number;
  status?: Fixture['status'];
  [key: string]: unknown;
}

export interface ValueBet {
  match: string;
  market: string;
  odds: number;
  modelProbability: number;
  expectedValue: number;
  fixtureId?: string;
  league?: string;
  startTime?: string;
  [key: string]: unknown;
}

export interface ModelInfo {
  version: string;
  roi: number;
  logLoss: number;
  status: 'active' | 'ready' | 'training';
  [key: string]: unknown;
}

export interface PipelineSnapshot {
  snapshotId?: number | null;
  reason?: string | null;
  capturedAt?: string | null;
  ageSec?: number | null;
  fixtureCount: number;
  oddsCount: number;
  marketLineCount: number;
  predictionCount: number;
  valueBetCount: number;
  modelVersion: string;
}

export interface PipelineStatus {
  snapshot: PipelineSnapshot;
  model: { version: string; evThreshold: number };
  pipeline: { streamerEnabled: boolean; alertEngineEnabled: boolean; snapshotIntervalSec: number };
}

export interface MatchEvent {
  minute: number;
  description: string;
  type: 'goal' | 'card' | 'substitution' | 'info';
}

export interface BetJournalEntry {
  id: number;
  created_at: string;
  fixture_ids: string[];
  league: string;
  league_id?: string;
  home_team: string;
  away_team: string;
  market: string;
  line?: number | null;
  side: string;
  model_probability: number;
  fair_odds?: number | null;
  bookmaker_odds?: number | null;
  ev: number;
  correlation_risk: number;
  confidence: number;
  stake: number;
  stake_rule?: string | null;
  status: string;
  result?: string | null;
  realized_roi?: number | null;
  closing_odds?: number | null;
  [key: string]: unknown;
}

export interface PerformanceBreakdown {
  label: string;
  roi: number;
  hitRate: number;
  count: number;
}

export interface PerformanceKpis {
  totalBets: number;
  wins: number;
  losses: number;
  pushes: number;
  pending: number;
  roi: number;
  yield: number;
  hitRate: number;
  avgEv: number;
  avgRealizedRoi: number;
  clvProxy: number;
  varianceProxy: number;
  maxDrawdown: number;
  currentDrawdown: number;
  drawdownCurve: { idx: number; equity: number; drawdown: number }[];
  roiCurve: { timestamp: string; roi: number }[];
  byMarket: PerformanceBreakdown[];
  byLeague: PerformanceBreakdown[];
  byTeam: PerformanceBreakdown[];
  windows: Record<string, { count: number; roi: number; hitRate: number }>;
  dataQuality: { pending: number; missing_results: number };
}

export interface BacktestRuleRequest {
  markets: string[];
  min_ev: number;
  min_confidence: number;
  max_per_day: number;
  correlation_threshold: number | null;
  stake_model: string;
  base_stake: number;
  kelly_fraction: number;
  stake_cap?: number | null;
  use_fair_odds_if_missing: boolean;
  league_whitelist?: string[] | null;
  league_blacklist?: string[] | null;
  team_whitelist?: string[] | null;
}

export interface BacktestRequestPayload {
  start_date?: string;
  end_date?: string;
  seed?: number;
  rules: BacktestRuleRequest;
}

export interface BacktestMetrics {
  roi: number;
  yield: number;
  hitRate: number;
  maxDrawdown: number;
  currentDrawdown: number;
  totalStake: number;
  profit: number;
  sampleSize: number;
  drawdownCurve: { idx: number; equity: number; drawdown: number }[];
  returns: number[];
  missingResults: number;
  correlationImpact: { withFilter: number; withoutFilter: number };
  honesty: { warnings: string[]; dataCompleteness: number };
  sensitivity: { evThreshold: number; roi: number }[];
}

export interface BacktestRun {
  id: number;
  status: string;
  params: Record<string, unknown>;
  metrics?: BacktestMetrics;
  warnings?: string[];
  seed: number;
  startedAt?: string | null;
  completedAt?: string | null;
  [key: string]: unknown;
}

export interface BetSlipRequest {
  schemaVersion: string;
  slipId: string;
  mode: string;
  selections: Array<{
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
  }>;
  correlationAlpha: number;
}

export interface BetSlipAnalysisResponse {
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
  report: {
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
  metadata: Record<string, unknown>;
}
