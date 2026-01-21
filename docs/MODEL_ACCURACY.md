# Model Accuracy & Performance

This document provides information about the prediction accuracy and performance metrics of the G.F.P.S (Global Football Probability System) models.

## Understanding Prediction Accuracy

**Important:** Football match prediction is inherently probabilistic. No system can predict match outcomes with 100% accuracy due to the unpredictable nature of sports. GFPS focuses on providing well-calibrated probabilities rather than guarantees.

## Model Types & Metrics

GFPS uses three main prediction models:

### 1. 1X2 Full-Time Result (Match Outcome)
Predicts whether the match ends in a home win (1), draw (X), or away win (2).

**Evaluation Metrics:**
- **Accuracy**: Percentage of correct predictions (typical range: 50-55%)
- **Brier Score**: Measures probability calibration quality (lower is better, typical range: 0.20-0.25)
- **Log Loss**: Penalizes confident wrong predictions (lower is better, typical range: 0.90-1.10)

**Performance Baseline:**
- Random guessing: ~33% accuracy
- Market odds baseline: ~45% accuracy
- GFPS target: 50-55% accuracy with well-calibrated probabilities

### 2. Over/Under 2.5 Goals
Predicts whether total goals will be over or under 2.5.

**Evaluation Metrics:**
- **Accuracy**: Percentage of correct O/U predictions (typical range: 55-60%)
- **Brier Score**: Probability calibration (typical range: 0.22-0.26)
- **Log Loss**: Confidence penalty (typical range: 0.60-0.70)

**Performance Baseline:**
- Random guessing: 50% accuracy
- GFPS target: 55-60% accuracy

### 3. Both Teams to Score (BTTS/GG)
Predicts whether both teams will score at least one goal.

**Evaluation Metrics:**
- **Accuracy**: Percentage of correct BTTS predictions (typical range: 60-65%)
- **Brier Score**: Probability calibration (typical range: 0.20-0.24)
- **Log Loss**: Confidence penalty (typical range: 0.55-0.65)

**Performance Baseline:**
- Random guessing: 50% accuracy
- GFPS target: 60-65% accuracy

## What Makes Good Football Predictions?

### Calibration Over Raw Accuracy
GFPS prioritizes **probability calibration** over raw accuracy. A well-calibrated model means:
- When the model says 60% probability, the outcome happens ~60% of the time
- Probabilities reflect true uncertainty rather than overconfident predictions
- Better long-term value detection for betting strategies

### Why Accuracy Alone Is Misleading
- **Football is low-scoring**: A 1-0 result vs 2-1 can dramatically change the outcome despite similar match dominance
- **Variance is high**: The better team doesn't always win
- **Context matters**: Form, injuries, motivation all impact results
- **Market efficiency**: Bookmaker odds already incorporate significant information

### Expected Value (EV) Focus
Rather than just predicting outcomes, GFPS focuses on **Expected Value (EV)**:
```
EV = (model_probability * odds) - 1
```
Positive EV indicates potential value opportunities where the model believes the probability is higher than the odds suggest.

## Model Methodology

GFPS combines multiple approaches for robust predictions:

1. **Poisson Distribution**: Base goal probability modeling
2. **Dixon-Coles Adjustment**: Correction for low-scoring matches
3. **Team Strength Ratings**: Attack and defense multipliers by league
4. **Recent Form Weighting**: Last 5-10 matches influence
5. **Market Calibration**: Blending model outputs with market odds (overround and Shin de-vigging)
6. **Temperature Scaling**: Probability calibration to maintain coherent distributions

## Evaluating Model Performance

To evaluate the models yourself, you can run:

```bash
# Requires historical match data in the database
source .venv/bin/activate
python scripts/ml_eval.py
```

This will output:
- Classification accuracy for each model
- Brier scores (calibration quality)
- Log loss (probability quality)
- Detailed classification reports

## Performance Tracking

GFPS includes built-in performance tracking features:

- **ROI Tracking**: Return on investment for simulated betting strategies
- **Hit Rate**: Win percentage of predictions
- **Calibration Curves**: Visual representation of probability calibration
- **Drawdown Analysis**: Maximum equity drops over time
- **CLV (Closing Line Value)**: How predictions compare to final market odds

See [PERFORMANCE_TRACKING.md](PERFORMANCE_TRACKING.md) for details on using these features.

## Realistic Expectations

### What GFPS Can Do
✅ Provide well-calibrated probabilities for match outcomes  
✅ Identify potential value bets through EV analysis  
✅ Track performance metrics over time  
✅ Offer transparency in prediction methodology  
✅ Support backtesting and strategy validation  

### What GFPS Cannot Do
❌ Guarantee profitable betting outcomes  
❌ Predict with 100% accuracy  
❌ Account for unknown factors (injuries, motivation, referee decisions)  
❌ Overcome fundamental uncertainty in sports  
❌ Replace proper bankroll management and risk assessment  

## Comparison to Industry Standards

Football prediction models in the industry typically achieve:
- **1X2 Accuracy**: 48-55% (GFPS target: 50-55%)
- **Brier Score**: 0.20-0.30 (GFPS target: <0.25)
- **Profitable EV Detection**: Highly variable, depends on market inefficiencies

GFPS aims to be competitive with commercial prediction systems while maintaining transparency and free operation.

## Continuous Improvement

Model performance can be improved by:
- **More training data**: Historical matches with accurate odds
- **Feature engineering**: Additional team stats, player data, weather, etc.
- **Ensemble methods**: Combining multiple model types
- **Market-specific tuning**: Different models for different leagues
- **Real-time data**: Live match statistics and in-play modeling

See [scripts/ml_retrain.py](../scripts/ml_retrain.py) to retrain models with new data.

## Disclaimer

⚠️ **Important Risk Notice**

GFPS provides **probabilistic analytics only**, not guarantees or financial advice. Football outcomes remain uncertain. Past performance does not guarantee future results. Use GFPS responsibly and within your risk tolerance.

No prediction system can overcome the fundamental uncertainty and variance inherent in football matches. Always bet responsibly and never wager more than you can afford to lose.

---

## Additional Resources

- [LIMITATIONS.md](LIMITATIONS.md) - System limitations and transparency
- [BACKTESTING.md](BACKTESTING.md) - How to backtest strategies
- [PERFORMANCE_TRACKING.md](PERFORMANCE_TRACKING.md) - Track betting performance
- [METRICS_GLOSSARY.md](METRICS_GLOSSARY.md) - Explanation of all metrics
- [README.md](../README.md) - Main documentation

For questions about model accuracy or methodology, please open a GitHub issue.
