# Immutable Model Evaluation Records

Persist reviewed model evaluations here as `MODEL_EVAL-<scope>-<nnn>.md` (and referenced raw artifacts where applicable).

Every record binds `MODEL_EVAL_ID`, immutable `EVAL_ENV_ID` + environment digest/record, model/weights digest, runtime identity, test-set digest, parameter digest, repetitions, raw-result references, quality/performance/resource results, failures/limitations and review status.

`MODEL_EVALUATION.md` owns methodology only; it must not grow into a historical result log.
