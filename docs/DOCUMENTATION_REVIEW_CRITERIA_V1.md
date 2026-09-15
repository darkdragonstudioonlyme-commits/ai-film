# Documentation Review Criteria V1

DOC-REVIEW must review an immutable DOC-DESIGN commit and must not edit proposed documentation while reviewing.

## Acceptance cases

### DR-01 Cold start
Given only repository + workspace access and no transcript, reviewer can identify current mode/phase/work item, last durable candidate, current WIP, last review/open findings and exact next action.

### DR-02 Auto continue
Given user message `continue`, router selects the documented WIP/workflow without asking for already-known context.

### DR-03 WIP preservation
A durable base plus dirty documented WIP must route to resume WIP, not reset or formal review.

### DR-04 Stale remote cache
Reviewer must recognize that cached `origin/lane/*` is insufficient and require fresh fetch before consuming lane state.

### DR-05 Independent trust
IMPLEMENT/REVIEW and DOC-DESIGN/DOC-REVIEW have distinct permissions and immutable handoffs. Consumer cannot promote producer output based solely on producer labels.

### DR-06 Finding/block return path
Review finding, design gap, validation failure and user-required blocker each have deterministic return paths.

### DR-07 Self-learning
A reusable discovery has a memory entry format and a defined promotion path into standing policy without overriding reviewed contracts.

### DR-08 Git/artifact durability
Commit/package/artifact sequences define exact identity and remote verification; WIP is not mislabeled durable.

### DR-09 Documentation roadmap
Reviewer can explain what each core MD owns, what is historical, and what to update for state/next work/roadmap/policy/memory/workspace/review/delivery.

### DR-10 Anti-duplication
README and CHAT_HANDOFF do not pin mutable delivery versions; mutable facts have clear owning docs.

## Verdict

`PASS` requires DR-01…DR-10 all pass. Findings return to DOC-DESIGN and require a new immutable design commit before re-review.
