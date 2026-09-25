# Batch 015 — story coverage, continuity expectations, subtitle layout

T-047 story coverage:
- flattens screenplay beat intervals and shot timing into one 75s coverage map;
- every shot must fit wholly inside exactly one beat;
- every beat must contain at least one shot;
- shot runtime must reconcile to screenplay target; no orphan shot is silently accepted.

T-048 continuity expectations:
- compiles expected character state per shot/story_time directly from the continuity ledger;
- expectations are digest-bound;
- observed metadata must bind the exact expectation digest before diffing;
- intentional injury/prop/costume transitions already present in the ledger become the expected state rather than false drift;
- hair/age/body/costume/location mismatches suggest existing QC failure tags; other state mismatches remain explicit without inventing taxonomy.

T-049 subtitle layout:
- deterministic text-only layout planning for EN/ZH/VI × 9:16/16:9;
- checks cue duration, heuristic characters/second, max lines and aspect-specific safe box;
- text heuristics are not visual QC: every plan declares rendered-frame collision checking NOT_EVALUATED;
- no subtitle burn-in/render action is performed.
