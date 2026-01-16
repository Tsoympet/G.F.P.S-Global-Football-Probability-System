export type TrapRisk = 'low' | 'medium' | 'high';

export interface BookmakerContext {
  match: string;
  market: string;
  odds: number;
  modelProbability?: number;
  expectedValue?: number;
  fairOdds?: number;
  bookmakerOdds?: number;
  clv?: number;
  confidence?: number;
  startTime?: string;
  isLive?: boolean;
}

export interface TrapIndicator {
  level: TrapRisk;
  note: string;
}

export interface BookmakerVerdict {
  marketRead: string;
  riskAssessment: string;
  trapIndicators: TrapIndicator[];
  timingAdvice: string;
  confidenceWarning: string;
  limitations: string[];
}

const toPercent = (value?: number) => (value === undefined ? null : +(value * 100).toFixed(1));

export const buildBookmakerVerdict = (ctx: BookmakerContext): BookmakerVerdict => {
  const impliedProb = ctx.odds ? +(1 / ctx.odds).toFixed(3) : null;
  const modelProb = ctx.modelProbability ?? impliedProb ?? 0;
  const fairOdds = ctx.fairOdds ?? (modelProb ? +(1 / modelProb).toFixed(2) : null);
  const edge = modelProb && impliedProb ? +(modelProb - impliedProb).toFixed(3) : 0;
  const ev = ctx.expectedValue ?? (modelProb && ctx.odds ? modelProb * ctx.odds - 1 : undefined);

  const limitations: string[] = [];
  if (!ctx.clv) limitations.push('CLV snapshot missing; pricing drift unknown.');
  if (!ctx.startTime) limitations.push('Kickoff time missing; timing risk inferred statically.');
  limitations.push('No odds tape provided; line movement interpreted from static inputs only.');

  const trapIndicators: TrapIndicator[] = [];
  if (edge > 0.08 && (modelProb ?? 0) < 0.25) {
    trapIndicators.push({
      level: 'high',
      note: 'Market shade against low-probability outcome with unusually generous price.'
    });
  } else if (edge > 0.04) {
    trapIndicators.push({
      level: 'medium',
      note: 'Price sitting above implied fair suggests defensive margin or public fade.'
    });
  } else {
    trapIndicators.push({
      level: 'low',
      note: 'Price sits close to fair with limited apparent shading.'
    });
  }

  if ((ctx.confidence ?? 0) < 0.35) {
    trapIndicators.push({
      level: 'medium',
      note: 'Model confidence is thin; bookmaker can lean on margin without resistance.'
    });
  }

  const marketReadParts = [
    `Market: ${ctx.market}`,
    `Focus: ${ctx.match}`,
    `Model: ${toPercent(modelProb) ?? 'n/a'}% vs implied ${toPercent(impliedProb) ?? 'n/a'}%`,
    `Fair: ${fairOdds ? fairOdds.toFixed(2) : 'n/a'} vs book ${ctx.bookmakerOdds ?? ctx.odds}` // bookmakerOdds is feed price; odds is fallback/display.
  ];

  const riskAssessment = [
    ev !== undefined ? `Edge signal: ${(ev * 100).toFixed(1)}%` : 'Edge signal unavailable',
    ctx.clv !== undefined ? `CLV proxy: ${(ctx.clv * 100).toFixed(1)}%` : 'CLV proxy unavailable',
    ctx.isLive ? 'Live feed — volatility elevated.' : 'Pre-match — liquidity building.'
  ].join(' | ');

  const timingAdvice = ctx.startTime
    ? `Kickoff: ${ctx.startTime}. Without tape, treat late steam cautiously; numbers could be stale.`
    : 'Kickoff unknown; avoid assuming current price freshness.';

  const confidenceWarning = [
    'Analysis perspective only — not execution advice.',
    (ctx.confidence ?? 0) >= 0.65
      ? 'Confidence signal is steady but still bounded by model error.'
      : 'Confidence is constrained; prioritize risk buffers over headline edge.',
    'Public bias or news shock can invalidate static inputs quickly.'
  ].join(' ');

  return {
    marketRead: marketReadParts.join(' | '),
    riskAssessment,
    trapIndicators,
    timingAdvice,
    confidenceWarning,
    limitations
  };
};
