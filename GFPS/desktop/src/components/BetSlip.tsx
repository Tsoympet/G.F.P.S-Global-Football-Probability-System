/**
 * Bet Slip Component - SIMULATION/ANALYSIS MODE ONLY
 * 
 * Bottom drawer for bet slip accumulator analysis.
 * NO REAL BETTING OR MONEY EXECUTION.
 */

import { useBetSlipStore, BetSlipSelection } from '@store/betslip';
import { api } from '@api/client';
import { palette } from '@theme/palette';
import { useState } from 'react';

export const BetSlip = () => {
  const {
    selections,
    mode,
    isOpen,
    showAnalysis,
    analysisData,
    isAnalyzing,
    analysisError,
    removeSelection,
    clearSlip,
    setMode,
    toggleOpen,
    setShowAnalysis,
    setAnalysisData,
    setIsAnalyzing,
    setAnalysisError,
  } = useBetSlipStore();

  const [correlationAlpha, setCorrelationAlpha] = useState(1.0);

  const handleAnalyze = async () => {
    if (selections.length === 0) {
      setAnalysisError('No selections to analyze');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisError(null);
    setShowAnalysis(false);

    try {
      const request = {
        schemaVersion: '1.0',
        slipId: `slip-${Date.now()}`,
        mode,
        selections: selections.map(s => ({
          clientSelectionKey: s.clientSelectionKey,
          fixtureId: s.fixtureId,
          homeTeam: s.homeTeam,
          awayTeam: s.awayTeam,
          league: s.league,
          leagueId: s.leagueId,
          startTime: s.startTime,
          marketType: s.marketType,
          marketName: s.marketName,
          line: s.line,
          outcome: s.outcome,
          oddsBookmaker: s.oddsBookmaker,
          oddsFair: s.oddsFair,
          modelProbability: s.modelProbability,
        })),
        correlationAlpha,
      };

      const response = await api.analyzeBetSlip(request);
      setAnalysisData(response);
      setShowAnalysis(true);
    } catch (error: any) {
      setAnalysisError(error?.message || 'Failed to analyze bet slip');
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (!isOpen) {
    return (
      <div
        onClick={toggleOpen}
        style={{
          position: 'fixed',
          bottom: 0,
          right: 20,
          background: palette.cardElevated,
          border: `1px solid ${palette.border}`,
          borderBottom: 'none',
          borderRadius: '8px 8px 0 0',
          padding: '8px 16px',
          cursor: 'pointer',
          zIndex: 1000,
          boxShadow: '0 -2px 8px rgba(0,0,0,0.2)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ fontSize: 14, fontWeight: 600 }}>
            📊 Bet Slip ({selections.length})
          </div>
          <div
            style={{
              fontSize: 10,
              background: palette.warning,
              color: palette.textPrimary,
              padding: '2px 6px',
              borderRadius: 4,
              fontWeight: 700,
            }}
          >
            SIMULATION
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        background: palette.cardElevated,
        border: `1px solid ${palette.border}`,
        borderBottom: 'none',
        borderRadius: '8px 8px 0 0',
        maxHeight: '70vh',
        overflow: 'auto',
        zIndex: 1000,
        boxShadow: '0 -4px 12px rgba(0,0,0,0.3)',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: 12,
          borderBottom: `1px solid ${palette.border}`,
          position: 'sticky',
          top: 0,
          background: palette.cardElevated,
          zIndex: 10,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700 }}>
            📊 Bet Slip Analysis
          </h3>
          <div
            style={{
              fontSize: 11,
              background: palette.warning,
              color: palette.textPrimary,
              padding: '3px 8px',
              borderRadius: 4,
              fontWeight: 700,
            }}
          >
            SIMULATION / ANALYSIS ONLY
          </div>
          <div style={{ fontSize: 12, color: palette.textSecondary }}>
            ({selections.length} selections)
          </div>
        </div>
        <button
          onClick={toggleOpen}
          style={{
            background: 'transparent',
            border: 'none',
            color: palette.textSecondary,
            cursor: 'pointer',
            fontSize: 20,
          }}
        >
          ✕
        </button>
      </div>

      {/* Content */}
      <div style={{ padding: 16 }}>
        {selections.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              padding: 40,
              color: palette.textSecondary,
            }}
          >
            No selections added yet. Click "+ Add to Bet Slip" on value bets to get started.
          </div>
        ) : (
          <>
            {/* Mode selector */}
            <div style={{ marginBottom: 16, display: 'flex', gap: 8 }}>
              <button
                onClick={() => setMode('single')}
                style={{
                  padding: '6px 12px',
                  background: mode === 'single' ? palette.primary : palette.background,
                  color: mode === 'single' ? palette.textPrimary : palette.textSecondary,
                  border: `1px solid ${palette.border}`,
                  borderRadius: 6,
                  cursor: 'pointer',
                  fontSize: 13,
                }}
              >
                Single
              </button>
              <button
                onClick={() => setMode('accumulator')}
                style={{
                  padding: '6px 12px',
                  background: mode === 'accumulator' ? palette.primary : palette.background,
                  color: mode === 'accumulator' ? palette.textPrimary : palette.textSecondary,
                  border: `1px solid ${palette.border}`,
                  borderRadius: 6,
                  cursor: 'pointer',
                  fontSize: 13,
                }}
              >
                Accumulator
              </button>
            </div>

            {/* Selections list */}
            <div style={{ marginBottom: 16 }}>
              {selections.map((sel) => (
                <div
                  key={sel.clientSelectionKey}
                  style={{
                    padding: 12,
                    background: palette.background,
                    border: `1px solid ${palette.border}`,
                    borderRadius: 6,
                    marginBottom: 8,
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      marginBottom: 6,
                    }}
                  >
                    <div style={{ fontWeight: 600, fontSize: 13 }}>
                      {sel.homeTeam} vs {sel.awayTeam}
                    </div>
                    <button
                      onClick={() => removeSelection(sel.clientSelectionKey)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: palette.danger,
                        cursor: 'pointer',
                        fontSize: 16,
                      }}
                    >
                      ✕
                    </button>
                  </div>
                  <div
                    style={{
                      fontSize: 12,
                      color: palette.textSecondary,
                      marginBottom: 4,
                    }}
                  >
                    {sel.marketName} - {sel.outcome}
                  </div>
                  <div style={{ display: 'flex', gap: 16, fontSize: 12 }}>
                    <div>
                      <span style={{ color: palette.textSecondary }}>Odds: </span>
                      <span style={{ fontWeight: 600 }}>{sel.oddsBookmaker.toFixed(2)}</span>
                    </div>
                    {sel.modelProbability && (
                      <div>
                        <span style={{ color: palette.textSecondary }}>Prob: </span>
                        <span>{(sel.modelProbability * 100).toFixed(1)}%</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                style={{
                  flex: 1,
                  padding: '10px 16px',
                  background: palette.success,
                  color: palette.textPrimary,
                  border: 'none',
                  borderRadius: 6,
                  cursor: isAnalyzing ? 'not-allowed' : 'pointer',
                  fontSize: 14,
                  fontWeight: 600,
                  opacity: isAnalyzing ? 0.6 : 1,
                }}
              >
                {isAnalyzing ? 'Analyzing...' : '📊 Analyze Slip'}
              </button>
              <button
                onClick={clearSlip}
                style={{
                  padding: '10px 16px',
                  background: palette.background,
                  color: palette.textSecondary,
                  border: `1px solid ${palette.border}`,
                  borderRadius: 6,
                  cursor: 'pointer',
                  fontSize: 14,
                }}
              >
                Clear
              </button>
            </div>

            {/* Error */}
            {analysisError && (
              <div
                style={{
                  padding: 12,
                  background: palette.danger,
                  color: palette.textPrimary,
                  borderRadius: 6,
                  fontSize: 13,
                  marginBottom: 16,
                }}
              >
                {analysisError}
              </div>
            )}

            {/* Analysis Report */}
            {showAnalysis && analysisData && (
              <div
                style={{
                  marginTop: 16,
                  padding: 16,
                  background: palette.background,
                  border: `1px solid ${palette.border}`,
                  borderRadius: 6,
                }}
              >
                <h4 style={{ margin: '0 0 12px', fontSize: 15, fontWeight: 700 }}>
                  Analysis Report
                </h4>

                {/* Executive Summary */}
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>
                    Executive Summary
                  </div>
                  <div style={{ fontSize: 12, color: palette.textSecondary, marginBottom: 8 }}>
                    {analysisData.report.executiveSummary.key_insight}
                  </div>
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(2, 1fr)',
                      gap: 8,
                      fontSize: 12,
                    }}
                  >
                    <div>
                      <span style={{ color: palette.textSecondary }}>Combined Odds: </span>
                      <strong>{analysisData.totals.combinedOddsDecimal.toFixed(2)}</strong>
                    </div>
                    <div>
                      <span style={{ color: palette.textSecondary }}>Risk: </span>
                      <strong style={{ 
                        color: analysisData.totals.volatilityMetrics.profile === 'high' ? palette.danger : 
                              analysisData.totals.volatilityMetrics.profile === 'medium' ? palette.warning : 
                              palette.success 
                      }}>
                        {analysisData.totals.volatilityMetrics.profile.toUpperCase()}
                      </strong>
                    </div>
                    <div>
                      <span style={{ color: palette.textSecondary }}>Prob (naive): </span>
                      <span>
                        {(analysisData.totals.combinedProbability.naiveIndependence * 100).toFixed(2)}%
                      </span>
                    </div>
                    <div>
                      <span style={{ color: palette.textSecondary }}>Prob (adjusted): </span>
                      <span>
                        {(analysisData.totals.combinedProbability.correlationAdjusted * 100).toFixed(2)}%
                      </span>
                    </div>
                    <div>
                      <span style={{ color: palette.textSecondary }}>EV (naive): </span>
                      <span style={{ 
                        color: analysisData.totals.expectedValueRoi.naive > 0 ? palette.success : palette.danger 
                      }}>
                        {(analysisData.totals.expectedValueRoi.naive * 100).toFixed(2)}%
                      </span>
                    </div>
                    <div>
                      <span style={{ color: palette.textSecondary }}>EV (adjusted): </span>
                      <span style={{ 
                        color: analysisData.totals.expectedValueRoi.correlationAdjusted > 0 ? palette.success : palette.danger 
                      }}>
                        {(analysisData.totals.expectedValueRoi.correlationAdjusted * 100).toFixed(2)}%
                      </span>
                    </div>
                  </div>
                  {analysisData.totals.effectiveLegs && (
                    <div style={{ fontSize: 12, marginTop: 8, color: palette.textSecondary }}>
                      Effective legs: {analysisData.totals.effectiveLegs.toFixed(2)} / {selections.length}
                    </div>
                  )}
                </div>

                {/* Correlation Warnings */}
                {analysisData.report.correlationWarnings.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>
                      ⚠️ Correlation Warnings ({analysisData.report.correlationWarnings.length})
                    </div>
                    {analysisData.report.correlationWarnings.slice(0, 3).map((w: any, i: number) => (
                      <div
                        key={i}
                        style={{
                          padding: 8,
                          background: palette.cardElevated,
                          borderLeft: `3px solid ${
                            w.severity === 'critical' ? palette.danger :
                            w.severity === 'high' ? palette.warning :
                            palette.border
                          }`,
                          borderRadius: 4,
                          marginBottom: 6,
                          fontSize: 11,
                        }}
                      >
                        <div style={{ fontWeight: 600, marginBottom: 4 }}>
                          {w.severity.toUpperCase()}: {w.description}
                        </div>
                        <div style={{ color: palette.textSecondary }}>{w.impact}</div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Professional Notes */}
                {analysisData.report.professionalNotes.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>
                      Professional Notes
                    </div>
                    {analysisData.report.professionalNotes.map((note: any, i: number) => (
                      <div
                        key={i}
                        style={{
                          padding: 8,
                          background: palette.cardElevated,
                          borderRadius: 4,
                          marginBottom: 6,
                          fontSize: 11,
                        }}
                      >
                        <div style={{ fontWeight: 600, marginBottom: 2, textTransform: 'uppercase', fontSize: 10 }}>
                          {note.category.replace('_', ' ')}
                        </div>
                        <div style={{ color: palette.textSecondary }}>{note.note}</div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Disclaimer */}
                <div
                  style={{
                    padding: 10,
                    background: palette.cardElevated,
                    borderRadius: 4,
                    fontSize: 10,
                    color: palette.textSecondary,
                    fontStyle: 'italic',
                  }}
                >
                  {analysisData.report.disclaimer}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
