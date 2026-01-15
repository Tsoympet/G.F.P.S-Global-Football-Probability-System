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
}

export interface LiveOddsRow {
  fixtureId?: string;
  market: string;
  home: number;
  draw: number;
  away: number;
  source?: string;
  startTime?: string;
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
  pricedProbabilities?: ProbabilitySet;
  finalOdds?: ProbabilitySet;
  modelVersion?: string;
  confidence?: number;
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
}

export interface ModelInfo {
  version: string;
  roi: number;
  logLoss: number;
  status: 'active' | 'ready' | 'training';
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
