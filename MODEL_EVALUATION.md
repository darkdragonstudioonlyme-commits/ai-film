# AI-FILM-SERVER — Model Evaluation Workflow

## Goal

Compare models for project business goals using reproducible workloads and exact environment identity, not anecdotal single generations.

## Entry gate

A model evaluation requires:

- an `EVAL_ENV_ID` from `SERVER_ENVIRONMENT.md` with all metrics needed by the evaluation;
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
