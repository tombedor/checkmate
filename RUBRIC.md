# Checkmate Evaluation Rubric

This rubric is tailored to the current Checkmate product: a chess improvement app that surfaces positions from a player's own games, turns them into interactive study challenges, and should help the player understand recurring weaknesses.

## How to score

Score each sub-dimension on a 0-5 scale:

- `0` = absent or actively harmful
- `1` = weak, inconsistent, or mostly unusable
- `2` = below bar, useful only in narrow cases
- `3` = solid baseline
- `4` = strong and consistently valuable
- `5` = exceptional, clearly best-in-class for this product stage

For each sub-dimension:

`weighted points = (score / 5) * weight`

Total score:

`sum(weighted points)` out of `100`

## Rubric

| Dimension | Weight | What this measures |
| --- | ---: | --- |
| UX and interaction quality | 35 | Whether the product is easy, clear, fast, and pleasant enough to support repeated study |
| Drill-down for chess improvement | 40 | Whether the user can move from a surfaced mistake to the underlying concept, pattern, phase, and actionable next step |
| Relevance of surfaced games and positions | 25 | Whether the app selects the right games, moments, and themes to study next |

## 1. UX and interaction quality (35)

| Sub-dimension | Weight | `0-1` | `3` | `5` |
| --- | ---: | --- | --- | --- |
| Core study flow clarity | 10 | User is unsure what to do next or what just happened | Challenge flow is understandable and mostly self-explanatory | Flow is obvious, low-friction, and supports rapid repetition without confusion |
| Board and move interaction | 8 | Input is buggy, ambiguous, or unpleasant | Move entry works reliably with minor rough edges | Move entry feels natural across click/drag/mobile and prevents avoidable mistakes |
| Feedback and reveal quality | 8 | Feedback is generic, delayed, or hard to parse | Reveals the right move and basic explanation clearly | Reveal is immediate, well-structured, and makes the lesson memorable |
| Navigation and queue management | 5 | Hard to move between puzzles or understand progress | User can progress through the queue and track basic status | Queue state, progress, filtering, and resume behavior all feel deliberate and trustworthy |
| Visual hierarchy and readability | 4 | Cluttered, inconsistent, or visually fatiguing | Readable with acceptable structure | Excellent hierarchy, scannability, and focus on the board/lesson at the right moments |

### UX scoring guidance

Give extra credit when the interface reduces cognitive overhead during study.

Deduct points when the UI makes the user think about the tool instead of the chess.

## 2. Drill-down for chess improvement (40)

| Sub-dimension | Weight | `0-1` | `3` | `5` |
| --- | ---: | --- | --- | --- |
| Concept diagnosis | 10 | Mistakes are labeled vaguely or incorrectly | Most surfaced mistakes are tied to a plausible concept | Concepts are precise, consistent, and teach the actual reason the move mattered |
| Root-cause analysis | 8 | Only shows the final blunder | Usually identifies the immediate mistake and some context | Regularly traces mistakes to the earlier decision that created the problem |
| Phase-specific insight | 6 | Opening/middlegame/endgame are treated the same | Some phase-aware framing exists | Analysis adapts meaningfully by phase and teaches the right vocabulary for each |
| Actionability of explanations | 8 | Explanations are descriptive but not useful | User can usually tell what to work on next | Explanations turn mistakes into concrete study plans, heuristics, or repeatable habits |
| Pattern aggregation across games | 8 | App feels like isolated puzzles | Some recurring weaknesses are summarized | User can clearly see repeated themes across multiple games and why they matter |

### Drill-down scoring guidance

This is the heart of the product. A polished puzzle UI with weak diagnosis should still score poorly here.

The standard is not just "can explain a move," but "can help the player improve a recurring weakness."

## 3. Relevance of surfaced games and positions (25)

| Sub-dimension | Weight | `0-1` | `3` | `5` |
| --- | ---: | --- | --- | --- |
| Personal relevance | 8 | Selected content feels random or generic | Most positions are recognizably tied to the user's own play | Surfaced content reliably reflects the player's actual habits, openings, and recurring errors |
| Improvement leverage | 8 | App surfaces low-value or noisy moments | Many selections are worth studying | The queue consistently prioritizes mistakes that matter most for rating improvement |
| Variety without drift | 4 | Repetitive in a bad way or scattered with no theme | Mix is acceptable | Strong balance between reinforcing real weaknesses and avoiding stale repetition |
| Ranking and prioritization logic | 5 | Ordering feels arbitrary | Ordering is somewhat sensible | Queue ordering clearly reflects frequency, severity, recency, and learning value |

### Relevance scoring guidance

High relevance means the user trusts that time spent in the queue is well spent.

A queue full of technically correct but low-leverage positions should lose points here.

## Scorecard template

Use this table during evaluation.

| Sub-dimension | Weight | Score (0-5) | Weighted points |
| --- | ---: | ---: | ---: |
| Core study flow clarity | 10 |  |  |
| Board and move interaction | 8 |  |  |
| Feedback and reveal quality | 8 |  |  |
| Navigation and queue management | 5 |  |  |
| Visual hierarchy and readability | 4 |  |  |
| Concept diagnosis | 10 |  |  |
| Root-cause analysis | 8 |  |  |
| Phase-specific insight | 6 |  |  |
| Actionability of explanations | 8 |  |  |
| Pattern aggregation across games | 8 |  |  |
| Personal relevance | 8 |  |  |
| Improvement leverage | 8 |  |  |
| Variety without drift | 4 |  |  |
| Ranking and prioritization logic | 5 |  |  |
| Total | 100 |  |  |

## Interpreting the total

- `90-100`: excellent; clearly effective as a focused chess improvement product
- `75-89`: strong; valuable product with a few meaningful gaps
- `60-74`: promising but uneven; useful in places, not yet consistently effective
- `40-59`: weak; some value exists, but important parts of the learning loop are underdeveloped
- `<40`: not yet meeting the bar for a reliable improvement tool

## Recommended evaluation method

Use at least one evaluator from each of these perspectives:

- product/UX
- chess improvement or coaching
- an actual user of the app

Run the evaluation on a real study session, not just a static walkthrough. Score after:

1. loading the queue
2. solving 5-10 challenges
3. reviewing at least one recurring weakness
4. checking whether the surfaced content feels worth the time spent
