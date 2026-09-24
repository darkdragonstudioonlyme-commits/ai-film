# Shot Compiler

Input: structured shot + continuity ledger + casting profile + render aspect.
Output: deterministic prompt bundle containing camera, action, character state, casting, dialogue, references, seed and negatives.
Persist structured source and compiled bundle; never keep only a human prompt.
The compiler must not silently drop injuries, costume damage, props or identity state.
Backend-specific adapters may transform this bundle after MODEL-EVAL without changing story semantics.
Acceptance: identical inputs compile byte-equivalent semantic content; integration test compiles all eight slice01 benchmark shots.
