# Workflow and verification

Contents: 1. Execution row · 2. Command shapes · 3. Minimum evidence ·
4. Manifest edits · 5. Feature and platform widening · 6. Required gates and
failures · 7. Scope escalation · 8. Final diff audit

## 1. Execution row

Read the repository sources that exist before choosing commands:

- `Cargo.toml` and inherited workspace package and lint tables;
- `rust-toolchain.toml` for the execution toolchain;
- package or inherited `rust-version` for the declared MSRV;
- `rustfmt.toml` or `.rustfmt.toml`, `clippy.toml`, `.cargo/config.toml` and
  any files it `include`s;
- `deny.toml`, cargo-vet's `supply-chain/`, CI workflows, and documented
  `justfile` or `Makefile` gates.

Record package, target, feature row, platform, toolchain, and MSRV separately.
Cargo aliases and task runners are conveniences; report the underlying command
when it matters to the evidence.

## 2. Command shapes

Adapt placeholders from repository evidence. Put package, target, and feature
selection before `--`; put rustc or Clippy lint flags after it.

```bash
cargo fmt --all --check
cargo clippy -p <package> <target-selection> <feature-selection> -- -D warnings
RUSTDOCFLAGS="-D warnings" cargo doc -p <package> --no-deps <feature-selection>
cargo deny check
cargo metadata --no-deps --format-version 1
cargo +<msrv> check -p <package> <target-selection> <feature-selection>
cargo check -p <package> --target <target-triple> <feature-selection>
```

Use `--all-targets` for Clippy when tests, examples, or benches changed. Add
`--locked` when a committed lockfile exists and the repository expects locked
resolution. Test commands are in `references/testing.md`.

On Cargo 1.97 or newer, `CARGO_BUILD_WARNINGS=deny` denies rustc, Clippy, and
rustdoc warnings in one setting; older Cargo ignores it, so MSRV rows keep
`-D warnings`. Make mass or mechanical rewrites with syntax-aware tools
(`cargo fix`, `cargo clippy --fix -p <package>`, rust-analyzer renames), then
audit the diff.

## 3. Minimum evidence

Each touched surface adds its row. These rows are the floor for `COMPLETE`
whenever the needed tools are available.

| Surface | Minimum evidence |
|---|---|
| Formatting only | rustfmt check |
| Private logic | Focused test exercising the change, scoped Clippy |
| Bug fix | Regression test that fails before the fix and passes after, scoped Clippy |
| New package or workspace member | rustfmt, Clippy on all targets, tests, rustdoc for the new package |
| Public API | Scoped Clippy, behavior tests, rustdoc, changed doctests; `cargo semver-checks` for published libraries when available |
| Guards, `Drop`, finalization | The lifecycle tests in `references/ownership-raii.md` |
| Async, threads, locks, atomics | Deterministic tests including cancellation and shutdown paths (`references/concurrency.md`) |
| `unsafe` or FFI | Safe-API tests plus Miri, a sanitizer, or a documented fallback |
| Documentation only | rustdoc; doctests when runnable examples change |
| Metadata-only manifest edit | `cargo metadata` |
| Lints, features, toolchain, profiles | Affected static baseline and the relevant feature or toolchain row |
| Dependencies or `deny.toml` | Affected build and test row, every configured `cargo deny` check |
| MSRV-sensitive change | Repository MSRV job or an explicit MSRV check |
| Generated or vendored code | Regenerate or patch upstream, then build the affected row |
| Cross-package behavior | Affected package and direct dependents; workspace when policy or reach requires it |
| Code review | Inspect contract, diff, tests, and claimed evidence; run risk-scoped checks when execution is allowed; list unrun checks |
| Release verdict | Every repository-required release row |

A behavior claim needs a test that exercises the touched behavior. Formatting,
prose, lint-only, and metadata changes need no new tests.

## 4. Manifest edits

| Edit class | Examples | Minimum evidence |
|---|---|---|
| Metadata-only | description, readme, authors, keywords | `cargo metadata` |
| Lint, toolchain, or feature policy | `[lints]`, features, `rust-version`, profiles | Affected static baseline and relevant rows |
| Dependency or supply chain | dependency source, version, features, lockfile, `deny.toml` | Affected build and test row plus configured deny checks |
| Target wiring | `[[bin]]`, examples, proc macros, build scripts, path dependencies | Checks and tests for each affected host or target boundary |

When an edit could be metadata-only or policy-changing, inspect its effect
through `cargo metadata`; if doubt remains, treat it as policy-changing.

## 5. Feature and platform widening

Run, or explicitly report as uncovered, every row the change can affect:

| Trigger | Required widening |
|---|---|
| `cfg(...)` or target-specific dependency | Relevant target triple and feature row |
| `no_std` or `alloc` boundary | `--no-default-features` and the supported target or build mode |
| Mutually exclusive features | One valid invocation per supported combination; never force `--all-features` |
| Optional runtime or backend | Each changed backend row and the shared default row |
| Proc macro | Host compilation plus a consumer or expansion test |
| Build script | Host execution, emitted configuration, environment inputs, `rerun-if-*` behavior |
| Platform FFI | Supported target build plus boundary tests, or a documented unavailable target |
| Shared workspace policy | Every inheriting member or the canonical workspace gate |

When `cargo-hack` is available, enumerate rows mechanically instead of
hand-picking them:

```bash
cargo hack check -p <package> --each-feature --no-dev-deps
cargo hack check -p <package> --feature-powerset --depth 2 --no-dev-deps
cargo hack check -p <package> --rust-version
```

`--each-feature` checks each feature alone, `--feature-powerset` checks
combinations (bound large sets with `--depth`), and `--rust-version` checks
against the declared MSRV.

Cross-compilation proves compilation, not runtime behavior on the target.

## 6. Required gates and failures

A gate is required only when at least one of these holds:

1. the repository contract declares it required;
2. the user requires its evidence;
3. the requested outcome is a verification or release verdict that cannot be
   established without it;
4. the change affects a supported row that no narrower evidence exercises.

Other checks this skill recommends are evidence, not gates. An unconfigured
optional tool (no `deny.toml`, no semver tooling) is not a gap, but never claim
its coverage.

When a command is missing or unusable, record the attempted command and its
diagnostic, run the best fallback that covers part of the same risk, and name
the surface still uncovered. Then choose the state:

| Situation | State |
|---|---|
| Optional tool unavailable, fallback covers the claim | `COMPLETE`; mention the omission when relevant |
| Relevant check unavailable, outcome does not depend on it | `COMPLETE WITH GAPS` |
| Required gate unavailable locally, CI is the authoritative pending runner | At best `COMPLETE WITH GAPS`; never claim it passed |
| Required gate fails with an introduced or affected failure | `BLOCKED` until fixed or the user changes the contract |
| Verification or release task needs an unavailable row | `BLOCKED` |

Classify every observed failure:

- **Introduced**: caused by the change. In a required gate: `BLOCKED`.
- **Affected pre-existing**: predates the change and involves the changed
  surface. Keep the scoped claim only when the change does not worsen the
  failure and the claim does not depend on the broken path; otherwise
  `BLOCKED` until fixed or the scope shrinks.
- **Unrelated pre-existing**: predates the change and does not involve the
  changed surface. Report it with evidence and keep the scoped claim.
- **Indeterminate**: no baseline distinguishes the cases. Build a narrower
  reproducer or report the gap; in a required gate it prevents `COMPLETE`.

A pre-existing classification needs baseline evidence: the same command failing
on the pre-change tree, or authoritative CI history. A failure involves the
changed surface when it exercises shared code, public API, features, or
dependencies of the change, not merely because its package is named in the
task.

## 7. Scope escalation

Escalate only as far as evidence requires: focused test, then the affected
package and feature row, then direct dependents or adjacent target rows, then
the workspace or release matrix. Widen immediately when repository policy
mandates a broader gate, a public contract crosses packages, shared build
policy changes, or narrow checks cannot exercise the claimed behavior.

## 8. Final diff audit

Before choosing a state:

1. Inspect the full diff and changed-file list; every file must belong to the
   requested or necessary scope.
2. Inspect manifest, feature, lockfile, visibility, public-API,
   lint-suppression, generated-file, and dependency deltas.
3. Remove debug output, secrets, placeholder code, stale comments, accidental
   formatting churn, and unrelated refactors.
4. Write comments, commit messages, and PR text for readers who never saw the
   session: no references to prompts, iterations, or discarded attempts.
5. Make sure the report describes the final diff, not an intermediate state.
