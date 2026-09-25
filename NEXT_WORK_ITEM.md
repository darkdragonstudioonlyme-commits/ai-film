# NEXT WORK ITEM — T-019 paid GPU benchmark gate

STATUS: BLOCKED
MILESTONE: M2
TASK: T-019 — launch the bounded rental-GPU benchmark and generate real casting/model evidence.

BLOCKER: EXPLICIT_PAID_GPU_APPROVAL_REQUIRED

PREPARED AND VERIFIED:
- exact model revisions/licenses/runtimes pinned
- RunPod rate snapshot hash-bound; 2026-09-25 Secure baseline: RTX 5090 USD 0.99/h, RTX Pro 6000 USD 2.09/h
- initial execution sub-cap proposal: USD 60
- full three-stage proposal hard cap: USD 150
- current repository authorization receipt: NOT_AUTHORIZED
- 32 casting jobs, blind scoring, worker/output manifests, asset ingestion and decision/cost ledger ready
- synthetic end-to-end fixtures prove control flow but are never production assets
- no standing authority to rent or spend

TO UNBLOCK:
The project owner must explicitly approve a bounded paid launch, including at minimum the maximum USD amount. At launch time the provider/GPU/rate snapshot is rechecked and bound into the authorization receipt.

AFTER APPROVAL:
1. Start with RTX 5090 stage A under the approved cap.
2. Run fixed smoke/casting population; download manifests/outputs/metrics.
3. Review OOM, quality, throughput and cost before any 96 GB stage.
4. Only escalate to RTX Pro 6000 if the measured decision gap justifies it.

DO NOT:
- launch/rent GPU before explicit bounded approval
- spend above the approved receipt
- bypass live-rate/model/license/runtime gates
- treat synthetic fixtures as generated film assets
- publish content
