# Parallel Bot Scenario Stages

Bot scenarios use one shared worktree. The coordinator owns `progress.md`, staging,
commits, and stage transitions. Before dispatch, record disjoint file manifests and
each path's baseline blob or absent marker. A path dirty before dispatch makes its
lane undispatchable.

## Stage 1 — Bot Acceptance RED and Interface Design

Dispatch bot acceptance RED and bot interface design concurrently. Acceptance owns
the isolated bot E2E test and its Statements/helpers. Design owns only shared handler,
logic, API-client, model, and test-interface surfaces; it implements no behavior.

Join both once. Reject a worker that staged, committed, edited `progress.md`, or
touched an undeclared path. Run combined checks, stage explicit paths, commit once,
and freeze the declared interfaces for Stage 2.

## Stage 2 — Bot Implementation Lanes

Build manifests from the frozen design and dispatch every non-trivial lane:

| Lane | Complete sequence | Owns |
|------|-------------------|------|
| Bot logic (`layer=bot-logic`) | RED → test review → GREEN → refactor | Bot-only logic and tests |
| API client (`layer=bot-api`) | RED → test review → GREEN → refactor | Typed HTTP client and tests |
| Handler (`layer=bot-handler`) | RED → test review → GREEN → refactor | Handlers, rendering, FSM, and tests |

Each lane preserves RED-before-GREEN and treats frozen Stage 1 interfaces as
read-only. A required interface or peer-manifest change fails with the conflicting
path and evidence. Skipped lanes are recorded; another lane never inherits their
paths implicitly.

Workers never stage, commit, or edit progress. Join each result once, reject paths
outside all manifests, run combined bot checks, then stage explicit paths and commit
once. Preserve successful disjoint lane checkpoints on failure or resume; invalidate
one only when its manifest, baseline, result hash, or check no longer matches.

## Stage 3 — Bot Acceptance GREEN and Independent Review

Require the committed Stage 2 join. Dispatch remove-marker-only bot acceptance GREEN
with `agent-review-agent` and `premortem-agent` over the immutable Stage 1+2 range.
Join all three before changing progress. Review workers never edit the tree.

On acceptance failure, keep Stage 3 current and identify the responsible Stage 2 lane
or seam; the verification lane never repairs production code. After GREEN, partition
review findings and apply SAFE fixes only after the join. Admitted cycle proposals use
the same explicit decision checkpoint as backend and frontend stages.

Bot acceptance is dispatcher-driven and isolated unless the Bot conventions declare
another harness. It never starts the deployed bot process or borrows API environment
variables. A real API interaction belongs to the Integration category.

## Progress Shape

```markdown
### 1.1 Scenario title
- [~] stage-1 bot acceptance RED + interface design
- [ ] stage-2 bot implementation lanes
- [ ] stage-3 bot acceptance GREEN + review
```
