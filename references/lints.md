# Lints

Contents: 1. Where policy lives · 2. Toolchain floors · 3. Ratchet ·
4. Suppressions and test exceptions · 5. Groups

## 1. Where policy lives

- **Manifest** (`[lints]` or `[workspace.lints]`): the source of truth. Every
  workspace member inherits with `[lints] workspace = true` unless an approved
  exception exists. Lint groups need a lower `priority` than individual lints
  (for example `{ level = "warn", priority = -1 }`), or Clippy's
  `lint_groups_priority` rejects the table.
- **Verification and CI** (`cargo clippy ... -- -D warnings`,
  `RUSTDOCFLAGS="-D warnings"`): promote warnings to failures. Preserve them in
  CI once they exist. `RUSTFLAGS` does not affect rustdoc warnings.
- **`clippy.toml`**: thresholds, `doc-valid-idents`, and the `allow-*-in-tests`
  keys. Clippy reads the MSRV from `rust-version`; set `msrv` only when it must
  differ.

A starter table for new projects is in `references/project-setup.md`.

## 2. Toolchain floors

| Construct | Floor | Fallback on an older MSRV |
|---|---|---|
| `#[expect(...)]`, lint `reason = "..."` | Rust 1.81 | `#[allow(...)]` with an adjacent comment |
| Manifest `[lints]` and `[workspace.lints]` | Cargo 1.74 | Crate-root `#![warn(...)]` / `#![deny(...)]` or lint flags in the verification command |
| TOML 1.1 manifest syntax (newlines or trailing commas in inline tables) | Cargo 1.94 | Single-line inline tables |
| Member `{ workspace = true, default-features = false }` | Cargo 1.99, edition 2024 member | `default-features = false` in `[workspace.dependencies]` |
| `raw_borrows_via_references` lint | Rust 1.99 | Omit; older compilers report an unknown lint |

Do not introduce syntax the declared MSRV rejects; keep the intent and report
the limitation.

## 3. Ratchet

Tighten in phases, enforcing in runtime code first and widening to tests once
the runtime surface is clean:

1. Core rustc and rustdoc lints: `unsafe_code` when desired,
   `rust_2018_idioms`, `unused_qualifications`, `unreachable_pub`, intra-doc
   link lints.
2. Clippy denials that mechanize hard rules: `dbg_macro`, `todo`,
   `unimplemented`, `unwrap_used`, `expect_used`, `panic`,
   `allow_attributes_without_reason`; with `unsafe` in scope,
   `undocumented_unsafe_blocks` and `multiple_unsafe_ops_per_block`.
3. Raise selected warn-level lints to deny only after real signal and with a
   cleanup path.
4. Trial individual `nursery` or `restriction` lints in focused modules before
   any repository-wide change.

When raising a lint to deny, make sure canonical verification and CI enforce it
and the migration cost is known. Never weaken an existing lint floor without
explicit approval (see `SKILL.md`).

## 4. Suppressions and test exceptions

- Scope every suppression as narrowly as possible and give it a reason.
  Prefer `#[expect]`, which fails once the lint no longer fires; use `#[allow]`
  when the lint fires only on some targets or feature rows.
- Acceptable reasons: an upstream false positive, a compiler or Clippy
  limitation, a known migration path with a cleanup plan, or a library API that
  intentionally takes a shape Clippy dislikes.
- Fix the shape instead of silencing `too_many_arguments`, clone lints, or docs
  lints (see `references/drift-control.md`). Never casually suppress
  correctness or safety lints.
- Package lints apply to every target. Test-only panics and unwraps need the
  `allow-unwrap-in-tests`, `allow-expect-in-tests`, `allow-panic-in-tests`, and
  `allow-dbg-in-tests` keys. They cover `#[test]` functions and items under
  `#[cfg(test)]`, not plain helper functions in `tests/`; mark a shared helper
  module with `#![cfg(test)]`. Do not claim tests are exempt without checking
  these keys and the lint table.

## 5. Groups

- Default to Clippy's standard groups plus the repository's explicit denials.
- `clippy::correctness` is deny-by-default for a reason; do not allow it.
- `clippy::pedantic` is a legitimate repository choice; enabling it means
  accepting targeted, reasoned `expect`s.
- Never enable `clippy::restriction` as a whole: its lints contradict each
  other and trip `blanket_clippy_restriction_lints`. Cherry-pick.
- Treat `clippy::nursery` as experimental; cherry-pick only.
- When a repository already enables one of these groups deliberately, keep its
  contract and surface noisy or contradictory results instead of overriding it.
