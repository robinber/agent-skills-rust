# Workflow and verification

Use this reference for verification scope, manifest edits, CI alignment, MSRV,
tool availability, and target or feature matrices. Apply the precedence and
completion states defined in `SKILL.md`.

## 1. Derive the execution row

Read the repository sources that exist before choosing commands:

- `Cargo.toml` and inherited workspace package/lint tables;
- `rust-toolchain.toml` for the default execution toolchain;
- package or inherited `rust-version` for declared MSRV;
- `.rustfmt.toml` or `rustfmt.toml`, `clippy.toml`, and
  `.cargo/config.toml`;
- `deny.toml`, CI workflows, and documented `justfile` or `Makefile` gates.

Record package, target, feature row, platform, toolchain, and MSRV separately.
Do not infer nightly, workspace-wide scope, or `--all-features`. Cargo aliases
and task runners are conveniences; report the underlying command when they
matter to the evidence.

If repository sources at this level disagree, stop the affected verification
or policy change. For example, CI and `AGENTS.md` disagreement is a policy
conflict, not permission to select the cheaper gate.

## 2. Canonical command shapes

Adapt placeholders from repository evidence. Put Cargo package, target, and
feature selection before `--`; put rustc or Clippy lint flags after `--`.

<!-- command-fixture: fmt-check -->
```bash
cargo fmt --all --check
```

<!-- command-fixture: clippy-scoped -->
```bash
cargo clippy -p <package> <target-selection> <feature-selection> -- -D warnings
```

<!-- command-fixture: rustdoc-scoped -->
```bash
RUSTDOCFLAGS="-D warnings" cargo doc -p <package> --no-deps <feature-selection>
```

<!-- command-fixture: cargo-deny -->
```bash
cargo deny check
```

<!-- command-fixture: cargo-metadata -->
```bash
cargo metadata --no-deps --format-version 1
```

<!-- command-fixture: msrv-check -->
```bash
cargo +<msrv> check -p <package> <target-selection> <feature-selection>
```

<!-- command-fixture: target-check -->
```bash
cargo check -p <package> --target <target-triple> <feature-selection>
```

Add `--locked` only when a committed lockfile exists and repository policy
expects locked resolution. A successful check on a newer pinned toolchain is
not proof of declared MSRV compatibility.

## 3. Verification layers

Select every layer touched by the claim:

| Surface | Minimum evidence |
|---|---|
| Formatting only | Repository rustfmt check |
| Private logic or bug fix | Focused regression test and scoped Clippy |
| Public API | Scoped Clippy, behavior tests, rustdoc, changed doctests |
| Metadata-only manifest edit | `cargo metadata`; formatting only if formatted sources changed |
| Lints, features, toolchain, profiles | Affected static baseline and relevant feature/toolchain row |
| Dependencies or `deny.toml` | Affected build/test row and every configured `cargo deny` check |
| Declared MSRV-sensitive change | Repository MSRV job or explicit MSRV check |
| Published-library compatibility | API review plus `cargo semver-checks` when configured or practical |
| Unsafe or FFI | Safe-API tests plus the strongest applicable dynamic/fallback checks |
| Cross-package/shared behavior | Affected package and direct dependents; workspace when policy or reach requires it |
| Release verdict | Every repository-required release row |

Tests remain impact-scoped for formatting, prose, lint-only, and pure metadata
changes. A behavior claim requires a test that exercises the touched behavior.
See `references/testing.md` for command ordering and test selection.

## 4. Manifest edit classes

Classify every manifest change before selecting gates:

| Edit class | Examples | Minimum verification |
|---|---|---|
| Metadata-only | description, readme, authors, keywords | `cargo metadata` |
| Lint/toolchain/feature policy | `[lints]`, features, `rust-version`, profiles | affected static baseline and relevant rows |
| Dependency/supply chain | dependency source/version/features, lockfile, `deny.toml` | affected build/test row plus configured deny checks |
| Target wiring | `[[bin]]`, examples, proc-macros, build scripts, path dependencies | checks/tests for each affected host or target boundary |

When uncertain whether an edit is metadata-only or policy-changing, inspect its
effect through Cargo metadata and choose the policy-changing class if ambiguity
remains.

## 5. Feature and platform widening

Run or explicitly leave uncovered the row that the change can affect:

| Trigger | Required widening |
|---|---|
| `cfg(...)` or target-specific dependency | Relevant target triple and feature row |
| `no_std` or `alloc` boundary | `--no-default-features` and the supported target/build mode |
| Mutually exclusive features | One valid invocation per supported combination; never force `--all-features` |
| Optional runtime/backend | Each changed backend row and shared default row |
| Proc macro | Host compilation plus a consumer/expansion test |
| Build script | Host execution, emitted config, environment inputs, and `rerun-if-*` behavior |
| Platform FFI | Supported target build plus boundary tests or documented unavailable target |
| Shared workspace policy | Every inheriting member or the canonical workspace gate |

Never present host/default-feature success as proof for an untested target,
backend, or feature combination. Cross-compilation proves compilation, not
runtime behavior on the target.

## 6. Unavailable tools and gates

Classify a missing or unusable command before selecting the final state:

1. Record the exact attempted command and diagnostic.
2. State whether the tool or row is optional guidance, relevant evidence, or a
   repository-required gate.
3. Run the best available fallback that covers part of the same risk.
4. Name the safety, compatibility, platform, or policy surface still uncovered.
5. Select the completion state from `SKILL.md`.

| Situation | State rule |
|---|---|
| Optional tool unavailable, fallback covers the requested claim | May remain `COMPLETE`; report the optional omission when relevant |
| Relevant check unavailable, work otherwise done, outcome does not require that proof | `COMPLETE WITH GAPS` |
| Required gate unavailable for implementation handoff but existing CI is the authoritative pending runner | At best `COMPLETE WITH GAPS`; never claim the gate passed |
| Required gate fails | `BLOCKED` until fixed or an exact scoped policy decision changes the contract |
| Release/verification task requires an unavailable row | `BLOCKED` |

This applies to Miri, sanitizers, `cargo deny`, `cargo semver-checks`, target
toolchains, external services, and machine-specific harnesses. Absence of an
unconfigured optional tool such as `deny.toml` is not itself a gap; falsely
claiming its coverage is prohibited.

## 7. Scope escalation

Escalate only when evidence requires it:

1. focused target or test;
2. affected package and feature row;
3. direct dependents or adjacent target rows;
4. workspace or release matrix.

Widen immediately when repository policy mandates a broader gate, a public
contract crosses packages, shared build policy changes, or narrow checks cannot
exercise the claimed behavior.
