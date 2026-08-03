# workflow

## 1. Source-backed guidance

- Start from the policy files that exist: `Cargo.toml` (package and/or workspace
  tables), `rust-toolchain.toml`, `.rustfmt.toml`, `clippy.toml`,
  `.cargo/config.toml`, and `deny.toml`. CI workflow files join the effective
  contract once they exist.
- Treat package or inherited `[workspace.package]` `rust-version` as the MSRV
  declaration. Treat `rust-toolchain.toml` as the default *execution* toolchain.
  They are not the same thing; both matter.
- Do not infer nightly by default. Use `+nightly` only for commands that
  explicitly require it (for example unstable rustfmt options already required by
  the repository).
- Run `rustfmt` before broad verification so the diff reflects behavior, not
  formatting drift.
- Check `.github/workflows/*` before widening scope when CI exists. Until then,
  use `AGENTS.md` and local policy files as the canonical gates and do not claim
  CI coverage.
- Verify from the smallest relevant scope first: one package, one test target,
  one feature set. Escalate only when the change affects shared code, feature
  gates, build scripts, or cross-package behavior.

## 2. Local verification baseline

Default verification is impact-scoped. Derive the full static baseline from the
repository; do not hardcode nightly or `--all-features`.

```bash
# fmt — repo toolchain; +nightly only if required
cargo fmt --all --check

# clippy — package/workspace and feature row from contract
cargo clippy -p <package> --all-targets <features-or-default> -- -D warnings

# docs
RUSTDOCFLAGS="-D warnings" cargo doc -p <package> --no-deps <features-or-default>

# supply chain — only if deny.toml exists; run ALL configured checks
cargo deny check
```

In a workspace, add `--workspace` (or explicit `-p` selection) when the change
spans members or shared policy. During iteration, package-scoped commands are
preferred.

**Feature rows:** default package features unless CI, `AGENTS.md`, or the change
requires another row (`--all-features`, `--no-default-features`, or explicit
`--features`). Mutually exclusive or platform-specific features must not be
forced under a single `--all-features` invocation.

Cargo aliases in `.cargo/config.toml`, when present, provide shorthand such as
`lint`, `doc-all`, `deny-all`, and `test-all`. Convenience targets in `justfile`
/ `Makefile` may wrap the same gates; always report the underlying cargo
commands when claiming verification.

Tests remain impact-scoped for lint, documentation, and policy-only changes. For
a behavior change claimed complete, run tests that exercise the touched
behavior. When runnable rustdoc examples change, also run scoped
`cargo test --doc`.

When reporting verification, copy the exact command shape and scope: package,
workspace/member selection, target (`--lib`, `--bin`, tests), feature set,
toolchain override if any, and whether doctests or dependency-policy checks were
included.

### MSRV

When `rust-version` is declared and the change is MSRV-sensitive (new APIs,
edition features, dependency bumps), verify with the repository's MSRV path —
for example `cargo +1.xx check -p <package>` or the documented CI MSRV job. A
green check on a newer pinned toolchain alone is not MSRV proof.

## 3. Manifest edit classes

Not every `Cargo.toml` edit is the same. Classify before choosing gates:

| Edit class | Examples | Minimum verification |
|---|---|---|
| Metadata-only | description, readme, authors, keywords | `cargo metadata --no-deps --format-version 1` (add `--locked` only if a committed lockfile exists and policy requires it) + `cargo fmt --all --check` if any Rust/fmt files also changed |
| Lint / toolchain / feature policy | `[lints]`, features, `rust-version`, profile policy | full static baseline for the affected package/workspace selection |
| Dependencies / supply chain | new deps, version bumps, `deny.toml` | full static baseline + `cargo deny check` when configured |
| Code-adjacent package wiring | new targets, `[[bin]]`, path deps | clippy + tests for the affected targets |

When in doubt between metadata-only and policy, use the stricter class.

## 4. Skill policy

- Always do an anchor pass over policy files and existing CI before editing.
- Prefer the narrowest command that can fail for the change you made.
- Escalate in this order when needed: package scope, `--all-targets`, the
  correct feature row, then workspace-wide selection.
- Treat the full static baseline as mandatory for lint, feature, toolchain,
  dependency-policy, and shared-package changes — not for pure metadata renames.
- Keep MSRV, lint policy, deny policy, and CI expectations aligned; if one
  changes, check the others.

## 5. Allowed exceptions

- If the change is pure formatting, `cargo fmt --check` is enough unless CI
  policy says otherwise.
- If the workspace is very large, first verify the affected package and direct
  dependents, then widen only if the change crosses package boundaries.
- For documentation-only edits, you may skip full test execution unless
  doctests or public API examples changed.
- If CI is the authoritative gate for a slow target, a local narrower check is
  acceptable as long as you clearly note the remaining gap.
- If no `deny.toml` exists, skip `cargo deny` and note the gap rather than
  inventing policy.
- If no lockfile is committed, do not pass `--locked`.
