---
name: rust-strict
description: >-
  Writes, reviews, and verifies release-quality Rust in Cargo packages and
  workspaces, following the repository's own policy (AGENTS.md, lints,
  toolchain, MSRV, CI). Use when creating a crate or workspace; implementing,
  fixing, refactoring, or porting code to Rust; reviewing Rust diffs; or
  changing Cargo.toml, dependencies, lints, unsafe/FFI, or release setup. Not
  for Rust questions answered without a repository.
---

# Rust Strict

Write Rust that a careful senior reviewer would merge, and claim only what you
verified. The repository's contract decides; this skill fills its gaps. Load
the detailed references only when the task touches their subject.

## Core rules

Integrity rules hold even against explicit approval:

- Never fabricate commands, results, coverage, compatibility, or review
  evidence.
- Never knowingly introduce undefined behavior.
- Never expose secrets in source, logs, errors, `Debug` output, argv, or
  reports.
- Never claim support for a target, feature row, toolchain, or MSRV you did not
  test.

Rust quality defaults, detailed in the references:

- Return typed errors through `?`. Outside tests, add `unwrap`, `expect`, or
  `panic!` only under the panic contract in `references/errors.md`; never ship
  `todo!` or `unimplemented!`. Never trade a panic for a silently discarded
  error (`let _ =`, `.ok()`, `unwrap_or_default()`).
- Borrow what you only read, own what you store, and never `clone()` just to
  silence the borrow checker.
- Make invalid states unrepresentable with enums carrying data, newtypes, and
  validation at construction; match exhaustively on enums you own.
- Keep the public surface minimal. Libraries never print to stdout or exit the
  process.
- Keep `unsafe` minimal, approved, and proved by a `// SAFETY:` comment.
- Keep Cargo features additive, and use the std facilities the declared MSRV
  allows instead of legacy crates. Never write a crate name, version, feature,
  or API from memory; use `cargo add`, read `cargo info`, and code against the
  resolved version's documentation.
- Never edit, delete, `#[ignore]`, or weaken a test to get a green run; when a
  test conflicts with the specification, stop and report it.
- Make the smallest coherent change. Do not add traits, generics, builders,
  features, or dependencies for hypothetical reuse.

## Rule strength

`must` and `never` block completion. `should` and `prefer` are defaults:
deviate when repository evidence or local design justifies it, and report
material deviations. `may` and `consider` never block. Do not promote a default
into a gate.

## Precedence

1. The integrity rules above.
2. Explicit user decisions.
3. The repository contract: applicable `AGENTS.md`, `CLAUDE.md`, and
   `CONTRIBUTING.md` (including any policy on AI-generated contributions),
   Cargo manifests and lint tables, `rust-toolchain.toml`, rustfmt and Clippy
   configuration, `.cargo/config.toml`, `deny.toml`, CI workflows, and task
   runners.
4. This skill's defaults.

When repository rules seem to disagree, a stricter nested rule adds to the
broader one, so satisfy both. A rule scoped to a narrower path or concern wins
inside that scope. A rule that relaxes another on the same scope and concern is
a conflict: stop the affected work, quote both rules, and ask. Never pick the
rule that merely permits more progress.

## Approval

Get explicit, scoped approval before you:

- add or widen `unsafe`; a task that names an unsafe or FFI surface approves
  only that surface (see `references/unsafe.md`);
- weaken any lint level, including `unsafe_code`, or relax `deny.toml`;
- change the declared MSRV;
- make a semver-breaking change to a published or reused API;
- add a git or wildcard dependency;
- edit generated or vendored code against repository policy.

Approval counts when the user names the deviation and its scope, or when the
repository contract documents it as a standing deviation with its scope (for
example "git dependencies allowed in `crates/proto`"). A generic request such
as "fix the build" is not approval. Record the approval you relied on. Approval
never covers the integrity rules, never proves safety, and never turns a
missing check into a pass. Without approval, stop that part of the work and
report `BLOCKED`.

## Before changing anything

1. Read the repository contract. Without CI, claim no CI coverage.
2. Identify the affected packages, targets, feature rows, and platform, the
   execution toolchain from `rust-toolchain.toml`, and the declared MSRV from
   `rust-version`. Never substitute one for the other.
3. Note public API, `unsafe`, dependency, generated or vendored code, and
   compatibility impact.
4. Select every matching row of the routing table; when several apply, satisfy
   all of them.
5. Decide the narrowest check that can fail for your claim and what would
   force widening it.

Read current code and configuration instead of assuming. Check
version-sensitive Cargo, Clippy, rustdoc, and std facts against official
documentation.

## Routing

| Task or surface | Read |
|---|---|
| Any code change | `references/workflow.md`, `references/testing.md`, `references/idioms.md` |
| New crate or workspace, or a repository without lint, toolchain, or CI policy | `references/project-setup.md`, `references/lints.md` |
| Code review | `references/review.md` plus the references matching the diff |
| Public API, traits, features, semver | `references/api-design.md`, `references/docs.md` |
| Errors, panics, `Result` design | `references/errors.md` |
| Guards, `Drop`, close, commit, shutdown | `references/ownership-raii.md` |
| Untrusted input, sizes, offsets, numeric conversions, limits | `references/correctness-safety.md` |
| `unsafe`, raw pointers, FFI | `references/unsafe.md` |
| Async, threads, locks, channels, atomics | `references/concurrency.md` |
| CLI, processes, streams, filesystem I/O | `references/cli-systems.md` |
| Dependencies, `deny.toml`, publishing | `references/dependencies-release.md` |
| Lints, toolchain, MSRV | `references/lints.md` |
| Documentation and doctests | `references/docs.md` |
| Large, duplicated, or heavily suppressed code | `references/drift-control.md` |

Target-specific code, build scripts, proc macros, `no_std`, and generated or
vendored code follow the widening rules in `references/workflow.md`.

## Verification

1. State the claim to prove: behavior, static policy, documentation,
   compatibility, supply chain, or a review finding.
2. Select package, target, features, platform, toolchain, and MSRV from
   repository evidence. Never infer nightly, workspace-wide scope, or
   `--all-features`.
3. Run the cheapest command that can fail for that claim, then add each layer
   the change touches. Command shapes are in `references/workflow.md` and
   `references/testing.md`.
4. Find repository gates that no scoped `cargo -p` run can fail: generated-file
   sync, pinned hashes, cross-crate scans, documentation that mirrors computed
   values. Run the ones that read the changed files, or report that surface as
   a gap.
5. Widen to dependents, the feature matrix, or the workspace only when shared
   impact or repository policy requires it.
6. Confirm the claimed tests actually ran: a filter that matches nothing still
   exits 0. A filtered test is not the suite, a host or default-feature run is
   not proof for other targets or features, and a pinned-toolchain run is not
   MSRV proof.

The minimum evidence for each touched surface in `references/workflow.md` is
the floor for `COMPLETE`. Beyond that floor, only the gates that
`references/workflow.md` defines as required can block. Classify every observed
failure as introduced, affected pre-existing, unrelated pre-existing, or
indeterminate before choosing a state. Never repair an unrelated failure out of
scope to get a green global run, and never claim that global gate passed. Run
the final diff audit in `references/workflow.md` before reporting.

## Report

- **COMPLETE**: the work is done, the floor verification ran, and every
  required gate passed.
- **COMPLETE WITH GAPS**: the work is done and no required gate is known to
  fail, but some relevant checks could not run. Not allowed when the requested
  outcome itself needs the missing evidence.
- **BLOCKED**: a conflict, missing approval, missing prerequisite, failing
  required gate, or outcome-critical missing check prevents a valid claim.

After code or manifest changes, end with:

```markdown
**State:** COMPLETE | COMPLETE WITH GAPS | BLOCKED — one-line reason
**Changed:** 1–5 bullets; flag public API, unsafe, MSRV, dependency, or feature impact
**Verified:** `exact command` → result (what it covers), one line each
**Not covered:** gaps, classified pre-existing failures, approvals relied on, follow-ups
```

Omit **Not covered** when it would be empty. Name targets, features, or
toolchains only when they are not the defaults. Answers that changed nothing
need no block. A review puts findings first (`references/review.md`) and states
which checks did not run.
