---
name: rust-strict
description: >-
  Apply release-quality engineering discipline when modifying, reviewing,
  debugging, documenting, or verifying an existing Rust package or Cargo
  workspace. Use for repository-backed Rust work involving Cargo policy,
  public APIs, ownership and resource lifecycles, errors, unsafe code, lints,
  tests, documentation, dependencies, MSRV, or release verification. Do not
  use for general Rust explanations, translation, summarization, or
  non-repository learning questions.
---

# Rust Strict

Use this skill to discover and enforce the contract of an existing Rust
repository. Keep the core workflow deterministic and load detailed Rust policy
from the routed references only when the task needs it.

The preferred suppression syntax (`#[expect(...)]`, lint reasons) assumes Rust
1.81+; manifest `[lints]` tables and workspace lint inheritance require Cargo
1.74+. On an older declared MSRV, preserve the same intent with syntax that MSRV
accepts and report the limitation. See `references/lints.md`.

## Normative language

Rules in this skill and its references use three enforcement levels:

- **HARD** (`must`, `must not`, `never`) — a correctness, integrity, safety, or
  explicit repository-contract rule. Violating it blocks completion unless the
  rule itself permits a scoped, operator-approved deviation.
- **DEFAULT** (`should`, `prefer`) — the expected engineering choice when
  repository evidence and local design do not justify another option. A
  justified local deviation does not block completion; report material
  deviations.
- **ADVISORY** (`may`, `consider`, `when practical`) — additional guidance that
  never blocks completion by itself.

Never promote a DEFAULT or ADVISORY rule into a hard gate. Bare imperatives in
the stop matrix, the completion contract, and the safety, panic, and integrity
contracts are HARD; unmarked guidance elsewhere is DEFAULT unless it protects
correctness, safety, or evidence integrity.

## Policy precedence

Apply these levels in order. A lower level fills gaps; it never silently
overrides a higher level.

1. **Non-overridable integrity and safety constraints**
   - Never fabricate commands, results, coverage, compatibility, or review
     evidence.
   - Never knowingly introduce undefined behavior.
   - Never expose secrets in source, logs, errors, debug output, commands, or
     reports.
   - Never claim support for an untested target, feature row, toolchain, or MSRV.
2. **Explicit operator decisions**
   - Allow a repository-policy deviation only when the operator names the exact
     deviation and its scope.
   - Do not treat a generic request such as "fix the feature" as approval to add
     `unsafe`, weaken lints, change MSRV, or break a public API.
   - Do not accept approval to fabricate evidence or knowingly ship unsound
     behavior.
3. **Repository contract**
   - Read applicable `AGENTS.md` and `CLAUDE.md` files.
   - Read Cargo manifests and lint tables, toolchain and formatter config,
     `clippy.toml`, `.cargo/config.toml`, `deny.toml`, CI workflows, and declared
     project gates.
4. **rust-strict defaults**
   - Apply this skill's defaults only when higher levels do not define a more
     specific rule.

Resolve apparent same-level disagreements by applicability before declaring a
conflict:

1. Determine the path, package, target, feature row, and code category each
   rule governs.
2. Apply the nearest path-scoped repository instruction to its scope; apply
   each manifest or tool configuration to the concern it governs.
3. Distinguish three cases: a nested rule that adds a stricter or additional
   gate is cumulative with the broader rule — run both; a nested rule that
   governs a narrower scope without contradicting the broader rule wins inside
   that scope while the broader rule still applies outside it; a nested rule
   that relaxes a broader rule on the same scope and concern is a conflict,
   never a specificity override.
4. Declare a conflict when two applicable rules impose incompatible outcomes —
   outcomes that cannot both be satisfied — on the same scope and concern.
   Then stop the affected work, quote both rules, and resume only after
   reconciliation or an exact operator decision establishes the scoped
   deviation. Never pick the rule that merely permits more progress.

## Explicit approval

Count approval only when a direct operator instruction identifies the deviation
and affected scope. Record the instruction in the final report. Approval may
authorize a documented repository-policy deviation; it does not prove safety,
waive required reporting, or turn a missing verification result into a pass.

Use these actions consistently:

- **Continue**: perform work already allowed by the effective contract.
- **Continue and report**: perform an allowed exception and record its scope.
- **Request explicit approval**: pause the affected work before making the
  deviation.
- **Refuse completion**: do not use `COMPLETE` while required evidence is
  missing or a required gate fails.
- **BLOCKED**: stop when approval, a prerequisite, policy reconciliation, or a
  required successful gate is necessary for the requested outcome.

## Stop and escalation matrix

| Situation | Required action | Completion consequence |
|---|---|---|
| Introduce new `unsafe` or expand an unsafe boundary | Apply the approval-scope rule in `references/unsafe.md` before editing; a task naming an unsafe/FFI surface approves only the minimal surface it names or necessarily implies, and every technical rule in that reference still applies | Without applicable approval: `BLOCKED` |
| Weaken `unsafe_code`, Rust, Clippy, rustdoc, or Cargo lint policy | Request exact approval and update the documented repository contract | Without approval, or if soundness would regress: `BLOCKED` |
| Relax `deny.toml` | Request exact approval and document the supply-chain rationale | Without approval: `BLOCKED` |
| Change declared MSRV | Request exact approval; align manifests, CI, and docs | Without approval: `BLOCKED` |
| Make a public semver-breaking change | Request exact approval for the named break | Without approval: `BLOCKED` |
| Add a git dependency or wildcard dependency | Request exact approval and report source/version risk | Without approval: `BLOCKED` |
| Skip or bypass a required verification gate | Do not claim it passed; use the best fallback and report the uncovered surface | `COMPLETE WITH GAPS`, or `BLOCKED` when that gate is required for the requested outcome |
| Add an internal invariant panic | Apply every condition of the canonical panic contract in `references/errors.md`; separate approval is needed only when repository policy forbids it or a caller-visible panic contract broadens | Any unmet contract condition: `BLOCKED` |
| Modify generated or vendor code contrary to repository policy | Request exact approval; prefer changing the generator or upstream source | Without approval: `BLOCKED` |
| Two applicable rules impose incompatible outcomes on the same scope and concern | Stop the affected work and quote both rules after the applicability resolution above | `BLOCKED` until reconciled |

## Anchor pass

Before editing, reviewing, debugging, or claiming verification:

1. Read applicable repository instructions and policy files from precedence
   level 3. If CI is absent, do not claim CI coverage.
2. Identify the package or workspace members, target kind, feature row, and
   platform affected.
3. Read the execution toolchain from `rust-toolchain.toml` when present. Read
   declared MSRV from package or inherited workspace `rust-version`; never
   substitute one for the other.
4. Identify public API, safety, generated/vendor, dependency, and compatibility
   impact.
5. Classify the task with the table below. Classification is additive, not
   exclusive: when a change matches several rows, load the union of their
   references, approval triggers, and verification layers. Never use the
   narrowest row to avoid a broader obligation from another affected surface.
6. Define the narrowest check that can falsify the claimed behavior and the
   conditions that require widening.

Resolve ambiguity by reading current code and configuration, not by inventing
architecture or policy from memory. Verify version-sensitive Cargo, Clippy,
rustfmt, rustdoc, API, and safety facts against official documentation.

## Task decision table

The anchor pass is mandatory for every row. "Minimum" means the least evidence
normally needed; repository gates and actual impact may require more.

| Task class | Mandatory references and anchor facts | Minimum verification and widening | Approval trigger |
|---|---|---|---|
| Implementation | `workflow.md`, `testing.md`; add domain references for touched code | Focused test plus scoped Clippy; widen for shared packages, features, targets, or public behavior | Any matrix deviation |
| Bug fix | `workflow.md`, `testing.md`; identify the failing invariant and regression surface | Reproduce or encode the failure, run the focused regression and scoped Clippy; widen when the bug crosses boundaries | Any matrix deviation |
| Code review | `workflow.md`, `review.md`, plus references matching the diff; record whether execution is authorized | Inspect contract, diff, tests, and claimed evidence; run risk-scoped checks when allowed; list unrun checks as gaps | Do not edit unless separately authorized |
| Public API change | `api-design.md`, `docs.md`, `errors.md`, `testing.md`; identify consumers and publication status | Scoped Clippy, tests, rustdoc/doctests; add semver checking for published or reusable libraries when practical | Any breaking change |
| Resource ownership, guards, RAII, or Drop | `workflow.md`, `ownership-raii.md`, `testing.md`; identify the resource owner, lifecycle states, and whether finalization is synchronous and infallible | Focused tests for normal completion, early return, explicit finalization, and fallback cleanup; widen for public API, concurrency, or unsafe impact | Public break, new unsafe, or policy deviation |
| Documentation-only | `docs.md`, `workflow.md`; distinguish prose from runnable examples | Rustdoc for public docs; add doctests when runnable examples change | Policy deviation only |
| Dependency change | `workflow.md`, `drift-control.md`, `dependencies-release.md`; inspect lockfile, source, features, licenses, and advisories | Affected build/test row plus every configured `cargo deny` check | Git/wildcard dependency or deny relaxation |
| Lint, toolchain, or MSRV policy | `workflow.md`, `lints.md`; align manifests, config, CI, and docs | Affected static baseline; exercise declared MSRV when changed or sensitive | Lint weakening or MSRV change |
| Unsafe or FFI | `unsafe.md`, `testing.md`; add `concurrency.md` for shared state or atomics | Focused safe-API tests plus Miri, sanitizer, or documented fallback as applicable | Any new or widened `unsafe` |
| Release verification | `workflow.md`, `testing.md`, `dependencies-release.md`, plus every domain reference implicated by the release | Execute the repository release matrix exactly; missing required evidence blocks an unqualified release verdict | Bypassing any required row |
| Generated or vendor code | `workflow.md`; identify generator, provenance, and repository edit policy | Validate regeneration or upstream patch and affected build row | Direct edit contrary to policy |
| Target-specific, proc-macro, build script, `no_std`, or `alloc` | `workflow.md`, `testing.md`; identify host/target split and exact feature row | Run the relevant target/feature row or report it as untested; host/default success is not proof | Unsupported compatibility claim |
| Async, locks, channels, atomics, or spawned tasks | `concurrency.md`, `testing.md`; add `api-design.md` for public contracts | Focused deterministic concurrency tests plus cancellation/shutdown paths where relevant | Public break, new unsafe, or policy deviation |

Load `drift-control.md` for non-trivial additions to large, duplicated,
suppressed, or already debt-sensitive surfaces. Load `cli-systems.md` when the
CLI/process/filesystem boundary changes. Load `correctness-safety.md` when the
change handles untrusted input, arithmetic on sizes/offsets/counts, numeric
conversions, or resource limits. Load `ownership-raii.md` when a change acquires
or releases a resource, introduces a guard or `Drop` implementation, or moves
fallible or asynchronous finalization behind a lifecycle API.

## Verification selection algorithm

1. State the exact claim to prove: behavior, static policy, documentation,
   compatibility, supply chain, or review finding.
2. Select package, target, feature row, platform, execution toolchain, and MSRV
   from repository evidence.
3. Run the cheapest command that can fail for that claim. Use the canonical
   command shapes in `references/workflow.md` and `references/testing.md`.
4. Add the relevant static, test, rustdoc/doctest, dependency, MSRV, semver,
   unsafe, or platform layer when the change touches that surface.
5. Widen from one target to package, feature matrix, dependents, or workspace
   only when shared impact or repository policy requires it.
6. Record each exact command, result, and coverage. Never describe a filtered
   test as a full suite or a host/default check as cross-platform proof.

If a tool is unavailable, follow the fallback and state-selection rules in
`references/workflow.md`. An unavailable optional tool is not automatically a
blocker; a failing required gate or missing evidence required by the requested
outcome is. A gate is required only per the definition in
`references/workflow.md`; never invent additional blocking conditions. The
decision-table minimum verification for the active task classes is the
completion floor, not optional evidence — "never invent blocking conditions"
applies only beyond that floor.

Classify every observed failure as introduced, affected pre-existing, unrelated
pre-existing, or indeterminate per `references/workflow.md` before selecting a
completion state. Never repair an unrelated pre-existing failure out of scope
merely to obtain a green global command, and never claim the global gate passed.

## Completion contract

Use exactly one state for non-trivial work:

- **COMPLETE** — The requested behavior is implemented or reviewed, the
  decision-table minimum verification for every applicable task class ran
  (unless the repository contract explicitly narrows it), and every required
  scoped gate passed.
- **COMPLETE WITH GAPS** — The requested work is done and no required gate is
  known to fail, but one or more relevant checks could not run. List every gap
  and uncovered surface. Do not use this state when the requested outcome itself
  requires the missing evidence.
- **BLOCKED** — A policy conflict, missing approval, unavailable prerequisite,
  failing required gate, or outcome-critical missing check prevents a valid
  completion claim.

Before selecting a state for any change, run the final diff audit in
`references/workflow.md`.

For non-trivial work, end with this schema; use `none` instead of omitting a
field and repeat the verification block once per executed command:

```markdown
STATE: COMPLETE | COMPLETE WITH GAPS | BLOCKED

## Scope
- package(s):
- target(s):
- feature row:
- toolchain:
- declared MSRV:
- public/API/safety impact:

## Changes or findings
- ...

## Verification
- exact command:
- result:
- coverage provided:
- claim covered:

## Baseline failures
- command:
- classification: introduced | affected pre-existing | unrelated pre-existing | indeterminate
- evidence and consequence:

## Gaps
- command not run:
- reason:
- uncovered surface:

## Deviations and approvals
- repository-policy deviations:
- explicit approvals:
- remaining follow-up:
```

Do not collapse a process gap into a content-success claim. A review may report
valid findings while remaining explicit that checks were not executed.

## Reference routing

Each detailed normative rule has one canonical reference. Load only the files
required by the task decision table.

| Canonical subject | Reference |
|---|---|
| verification scope, manifests, CI, MSRV, tools, target/feature matrices, failure classification, final diff audit | `references/workflow.md` |
| code review method, finding standard, and review output order | `references/review.md` |
| unit, integration, doctest, fixtures, property and command test shape | `references/testing.md` |
| Cargo/Rust/Clippy/rustdoc lint policy and suppressions | `references/lints.md` |
| public documentation and runnable examples | `references/docs.md` |
| public API and semver compatibility | `references/api-design.md` |
| typed errors and the sole panic contract | `references/errors.md` |
| ownership, RAII guards, Drop, and explicit finalization | `references/ownership-raii.md` |
| arithmetic, conversions, untrusted input, and resource bounds | `references/correctness-safety.md` |
| unsafe and FFI safety contracts | `references/unsafe.md` |
| async, threads, locks, channels, atomics, cancellation, shutdown | `references/concurrency.md` |
| CLI/process boundaries, streams, exit codes, secrets, filesystem and child-process I/O | `references/cli-systems.md` |
| dependency hygiene, supply chain, and publication verification | `references/dependencies-release.md` |
| size, duplication, suppressions, and no-net-new-debt defaults | `references/drift-control.md` |

Keep new edge-case policy in the canonical reference, not duplicated here.
