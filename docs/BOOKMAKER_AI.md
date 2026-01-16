# Bookmaker AI (Specialized Bookmaker Intelligence)

## What it is
- A bookmaker-style risk and pricing commentary engine.
- Challenges the model by explaining why a market might be priced the way it is.
- Surfaces margin placement, trap indicators, and timing risk from a desk perspective.

## What it is not
- Not a tipster, not financial advice, and not execution guidance.
- Does not promise profit or override the probability engine.
- Works from static inputs; no live trading or wagering actions exist in GFPS.

## Inputs considered
- Model probabilities and fair odds (derived).
- Bookmaker odds from the feed.
- Expected value signal and confidence flags.
- Optional CLV proxy when provided.
- Market type context (1X2 vs others) and live vs pre-match flag.

## Output shape
- **A. Market Read** – How the desk sees the pricing relationship.
- **B. Risk Assessment** – Edge, CLV proxy, and whether volatility is elevated.
- **C. Trap Indicators** – Desk-labelled risk bands (low/medium/high) with rationale.
- **D. Timing Advice** – Notes about stale numbers or steam risk.
- **E. Confidence Warning** – Explicit caution about model error and public bias.
- Limitations banner listing missing or assumed data.

## UI integration
- Exposed as **“Bookmaker View”** / **“Market Risk Commentary”** in the Value Bets screen.
- It is toggleable and **off by default** to avoid accidental activation.
- Requires a selected market; otherwise it surfaces a data limitation notice.

## How to interpret
- Treat the output as a second opinion to stress-test model edges.
- Use trap indicators to guard against public-team bias or shaded numbers.
- Timing advice flags stale or unconfirmed movement when odds tape is absent.

## Safety posture
- Avoids encouragement language (“bet”, “play”).
- Frames everything as analysis with explicit limitations.
- Reminds users to validate independently before any action.
