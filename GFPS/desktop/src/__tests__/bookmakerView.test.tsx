import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { BookmakerView } from '@components/BookmakerView';
import { buildBookmakerVerdict } from '@app/bookmakerAi';

describe('Bookmaker View', () => {
  const context = {
    match: 'Alpha FC vs Beta FC',
    market: 'Home Winner',
    odds: 2.4,
    modelProbability: 0.52,
    expectedValue: 0.248,
    fairOdds: 1.92,
    bookmakerOdds: 2.4,
    clv: 0.03,
    confidence: 0.68,
    startTime: '2026-01-16T18:32:55.030Z',
    isLive: false
  };

  it('builds a structured verdict without prohibited language', () => {
    const verdict = buildBookmakerVerdict(context);
    expect(verdict.marketRead).toContain('Alpha FC vs Beta FC');
    expect(verdict.riskAssessment).toContain('Edge signal');
    expect(verdict.trapIndicators.length).toBeGreaterThan(0);
    const serialized = [
      verdict.marketRead,
      verdict.riskAssessment,
      verdict.timingAdvice,
      verdict.confidenceWarning,
      verdict.trapIndicators.map((t) => t.note).join(' ')
    ]
      .join(' ')
      .toLowerCase();
    expect(serialized).not.toMatch(/\bbet\b/);
    expect(serialized).not.toMatch(/\bplay\b/);
  });

  it('respects visibility toggle and renders structured sections', () => {
    const { rerender } = render(<BookmakerView visible={false} context={context} />);
    expect(screen.queryByLabelText('Bookmaker View')).toBeNull();

    rerender(<BookmakerView visible context={context} />);
    expect(screen.getByText('Bookmaker View')).toBeInTheDocument();
    expect(screen.getByText(/A\. Market Read/i)).toBeInTheDocument();
    expect(screen.getByText(/C\. Trap Indicators/i)).toBeInTheDocument();
  });

  it('surfaces limitations consistently without flagging zero CLV as missing', () => {
    const withZeroClv = { ...context, clv: 0 };
    const verdictWithClv = buildBookmakerVerdict(withZeroClv);
    expect(verdictWithClv.limitations).toContain('No odds tape provided; line movement interpreted from static inputs only.');
    expect(verdictWithClv.limitations).not.toContain('CLV snapshot missing; pricing drift unknown.');

    const missingData = { ...context, clv: undefined, startTime: undefined };
    const verdictMissing = buildBookmakerVerdict(missingData);
    expect(verdictMissing.limitations).toContain('CLV snapshot missing; pricing drift unknown.');
    expect(verdictMissing.limitations).toContain('Kickoff time missing; timing risk inferred statically.');
  });
});
