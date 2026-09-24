# GPU rental benchmark proposal — 2026-09-24

Status: PROPOSAL ONLY. No resource has been launched and no spend is authorized by this document.

Baseline provider: RunPod Secure Cloud, chosen because a current public rate table is available for both target tiers. Recorded baseline rates are USD 0.99/hour for RTX 5090 32GB and USD 2.09/hour for RTX Pro 6000 96GB. Rates must be checked again immediately before any launch.

Staged plan over 3–5 calendar days:
1. Tier A — RTX 5090, at most 24 GPU-hours, compute ceiling USD 23.76.
2. Tier B — RTX Pro 6000, at most 12 GPU-hours, compute ceiling USD 25.08.
3. Finalist repeat — at most 24 GPU-hours; costed at the more expensive Pro 6000 rate, ceiling USD 50.16.

Worst-case compute ceiling is USD 99.00. Reserve USD 51.00 is held for temporary storage, egress, price drift, setup inefficiency and applicable provider charges. Proposed hard all-in authorization cap is USD 150.00.

The launch must stop before creation if the provider's live all-in projected charge cannot fit the USD 150 cap. Paid execution remains blocked until a bounded spend approval exists.

The benchmark uses the fixed slice01 profiles already in the repository. Model selection is based on blind quality scoring plus elapsed time, VRAM peak, failure/OOM rate and actual rental cost; one hero sample is not enough to select a winner.
