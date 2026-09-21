# AI-FILM-SERVER — Model Evaluation Workflow

## Goal

Compare models for project business goals using reproducible workloads and exact environment identity, not anecdotal single generations.

## Entry gate

A model evaluation requires:

- an immutable `EVAL_ENV_ID` / environment record from `environments/` with all metrics needed by the evaluation;
- exact model/version/weights identity;
- exact inference stack identity;
- reviewed evaluation objective and dataset/prompts;
- resource and quality metrics defined before running candidates.

Missing GPU/VRAM/runtime facts block GPU performance claims.

## Evaluation dimensions

For video/image/audio/model components choose relevant metrics from:

- output quality and requirement-specific rubric;
- temporal/identity consistency;
- instruction/prompt adherence;
- failure/rejection rate;
- deterministic/reproducible behavior where applicable;
- latency, throughput and warm/cold start;
- peak VRAM/RAM and OOM behavior;
- disk/model footprint and load time;
- recovery after OOM/interruption;
- compatibility with pipeline constraints;
- licensing/provenance/security constraints.

## Comparative protocol

```text
freeze objective + rubric + dataset
→ freeze environment
→ freeze inference parameters/seeds
→ warmup policy
→ run repeated candidate trials
→ record raw outputs + metrics + failures
→ analyze quality/resource tradeoff
→ independent review of recommendation
→ persist result bound to model + environment + test set
```

Do not tune one model against the benchmark after seeing results without rerunning comparable tuning for others or declaring a new experiment version.

## Result identity

```yaml
MODEL_EVAL_ID:
EVAL_ENV_ID:
MODEL_ID_AND_WEIGHT_DIGEST:
RUNTIME_ID:
TEST_SET_DIGEST:
PARAMETER_DIGEST:
REPETITIONS:
QUALITY_RESULTS:
PERFORMANCE_RESULTS:
RESOURCE_RESULTS:
FAILURES:
LIMITATIONS:
RECOMMENDATION:
REVIEW_STATUS:
```

A model recommendation is not a permanent policy. Re-evaluate when business goals, model versions or material environment inputs change.

## Persistence

Reviewed evaluation records live under `model-evaluations/`. The methodology file remains version-agnostic; historical results stay immutable and reference exact environment/model/test identities.

## Guarded quality improvement and promotion

Separate development/tuning samples from a held-out evaluation set grouped by story/character/scene so neighboring shots do not silently leak the same references across the boundary. Keep failures and rejected takes in the denominator. Freeze rubric and meaningful quality/cost thresholds before comparison; evaluate individual shots **and** sequence-level continuity, story comprehension, voice and editing.

Compare a candidate to the current champion with paired inputs and a declared seed/repetition policy; state uncertainty and nondeterminism. Human evaluation should hide candidate labels when practical. Automated similarity/quality scores are aids, not substitutes for story/continuity judgments or commercial rights clearance.

A promotion record binds prompt/compiler version, references, model/adapter/weights, dataset, workflow, environment, evaluation evidence, known regressions, rollback target and owner approval. Use a bounded canary workload before broad replacement; retain the old baseline and immutable generated assets. Runtime rollout implementation remains phase-gated. No model/GPU recommendation or speed claim is valid without the relevant measurements.

Before training or feedback reuse, record consent/rights, provenance, retention and allowed use of source stories, voices, likenesses and assets. Untrusted content, comments and model outputs are data, not authority to change policies, invoke tools or promote a model. Do not automatically ingest all production feedback into training.
