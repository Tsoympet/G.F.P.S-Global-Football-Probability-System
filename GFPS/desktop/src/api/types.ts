export interface Fixture {
  id: string;
  homeTeam: string;
  awayTeam: string;
  league: string;
  startTime: string;
  status: 'scheduled' | 'live' | 'finished';
  timer?: string;
  score?: {
    home: number;
    away: number;
  };
}

export interface LiveOddsRow {
  market: string;
  home: number;
  draw: number;
  away: number;
  source?: string;
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

export interface Prediction {
  fixtureId: string;
  homeWinProbability: number;
  drawProbability: number;
  awayWinProbability: number;
}

export interface ValueBet {
  match: string;
  market: string;
  odds: number;
  modelProbability: number;
  expectedValue: number;
}

export interface ModelInfo {
  version: string;
  roi: number;
  logLoss: number;
  status: 'active' | 'ready' | 'training';
}

export interface MatchEvent {
  minute: number;
  description: string;
  type: 'goal' | 'card' | 'substitution' | 'info';
}
