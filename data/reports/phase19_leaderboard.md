# Phase 19 Leaderboard — Eval Policy on Frozen ORB-W

Baseline incumbent: **64.3%** pass / **45.6%** pass+payout @ 1 micro.
Same trade ledger; only contract policy changes.

| Policy | WF Pass % | WF Pass+payout % | Holdout Pass % | Holdout P+p % |
| --- | --- | --- | --- | --- |
| fixed_1 | 62.9% | 43.8% | 59.1% | 37.6% |
| post_lock_2 | 58.7% | 41.0% | 54.7% | 34.8% |
| upshift_700_cap | 54.8% | 38.6% | 52.8% | 33.4% |
| skip_cushion_200 | 54.2% | 37.8% | 50.5% | 32.1% |
| upshift_800 | 54.1% | 37.9% | 50.0% | 31.5% |
| upshift_600_cap | 53.7% | 37.8% | 52.4% | 33.1% |
| post_lock_3 | 53.2% | 37.2% | 50.1% | 31.7% |
| upshift_700 | 52.9% | 37.1% | 49.5% | 31.2% |
| fixed_2 | 51.6% | 36.5% | 51.0% | 32.2% |
| downshift_600 | 51.1% | 35.9% | 48.9% | 30.9% |
| upshift_600 | 51.1% | 35.9% | 48.9% | 30.9% |
| upshift_500 | 50.1% | 35.3% | 47.5% | 29.9% |
| downshift_400 | 49.6% | 34.9% | 48.7% | 30.7% |
| upshift_400 | 49.6% | 34.9% | 48.7% | 30.7% |
| skip_cushion_300 | 48.6% | 34.0% | 45.6% | 29.0% |
| skip_cushion_400 | 41.1% | 28.8% | 39.9% | 25.4% |

## Challengers

_No policy clears +3pt pass lift with pass+payout ≥ baseline on WF._

## max_days sensitivity (fixed_1 + top policies)

| Policy | max_days | WF pass % | WF pap % |
| --- | --- | --- | --- |
| fixed_1 | 120 | 68.2% | 47.9% |
| fixed_1 | 90 | 67.7% | 47.6% |
| fixed_1 | 60 | 64.3% | 45.6% |
| post_lock_2 | 120 | 62.3% | 43.6% |
| post_lock_2 | 90 | 61.7% | 43.5% |
| post_lock_2 | 60 | 60.0% | 42.4% |
| skip_cushion_200 | 120 | 57.8% | 40.5% |
| upshift_700_cap | 120 | 57.3% | 40.6% |
| skip_cushion_200 | 90 | 56.9% | 40.5% |
| upshift_700_cap | 90 | 56.6% | 40.5% |
| skip_cushion_200 | 60 | 56.1% | 39.7% |
| upshift_700_cap | 60 | 56.0% | 39.9% |
