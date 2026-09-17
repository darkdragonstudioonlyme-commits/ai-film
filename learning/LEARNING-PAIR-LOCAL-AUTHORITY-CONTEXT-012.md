# LEARNING-PAIR-LOCAL-AUTHORITY-CONTEXT-012

LEARNING_ID: LEARNING-PAIR-LOCAL-AUTHORITY-CONTEXT-012
SCORE: 10
OBSERVED_AT_STATE: V42
TARGET_RELEASE: DOCSYS-V2-R9
CLASS: promoted-authority-semantic-context

## Observation

After historical/prior-tree R15/A15 promotion, the checker still allowed a mixed line where one historical verdict clause caused a separate stale/live verdict pair later on that line to be treated as historical too.

## Generalized learning

Historical/current authority classification belongs to each verdict-pair sentence or clause, never to the whole line. One historical marker cannot authorize or suppress a different pair elsewhere on the same line.

## Success metric

The next documentation promotion classifies historical/live review-audit authority per verdict-pair clause: a historical marker for one pair cannot mask a separate stale or stage-drift pair on the same line; DESIGN, REVIEW, AUDIT and PROMOTED checks all pass on one exact semantic tree.
