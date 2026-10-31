# Project setup

Contents: 1. Layout · 2. Toolchain and MSRV · 3. Starter lint policy ·
4. Dependencies and supply chain · 5. CI baseline · 6. Library documentation

Use this reference when creating a package, a workspace, or a new workspace
member, or when a repository has no lint, toolchain, or CI policy yet. In an
existing repository its contract wins; use this file only to fill gaps the
user asks you to fill.

## 1. Layout

- Start with one package. Split into a workspace when a second artifact
  (library, binary, proc macro) or a real dependency boundary appears, not for
  hypothetical reuse.
- Give a binary with testable logic a `lib.rs` next to `main.rs` and keep
  `main.rs` thin (see `references/cli-systems.md`).
- In a workspace, use a virtual root manifest, keep members under `crates/`
  named after the crate, and centralize shared metadata, dependency versions,
  and lints:

```toml
[workspace]
resolver = "3"
members = ["crates/*"]

[workspace.package]
edition = "2024"
rust-version = "<msrv>"
license = "MIT OR Apache-2.0"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
```

```toml
[package]
name = "my-crate"
version = "0.1.0"
edition.workspace = true
rust-version.workspace = true
license.workspace = true

[dependencies]
serde.workspace = true

[lints]
workspace = true
```

A virtual manifest has no edition, so set `resolver` explicitly. A member can
always add features to an inherited dependency. Removing default features the
workspace entry enables, with `{ workspace = true, default-features = false }`,
needs Cargo 1.99 and an edition 2024 member; when any toolchain that reads the
manifest, including the MSRV row, is older, set `default-features = false` in
`[workspace.dependencies]` and have members list what they need. A member
using `[lints] workspace = true` cannot override individual lints in its own
manifest; put a stricter crate-local rule at the crate root instead (for
example `#![forbid(unsafe_code)]`).

## 2. Toolchain and MSRV

- Set `rust-version` deliberately and check it in CI: for an application, the
  stable release you develop against; for a published library, the oldest
  toolchain you commit to test. Edition 2024 requires 1.85 or newer.
- Add `rust-toolchain.toml` only when the repository needs a fixed toolchain:

```toml
[toolchain]
channel = "<pinned-version>"
components = ["rustfmt", "clippy"]
```

  A pinned toolchain newer than `rust-version` does not prove MSRV
  compatibility; keep a separate MSRV row.
- Add a `rustfmt.toml` containing `style_edition = "2024"` so editors and bare
  `rustfmt` format like `cargo fmt` (bare `rustfmt` otherwise uses the 2015
  style); run `cargo fmt`, not `rustfmt`. Avoid nightly-only options unless the
  nightly requirement is documented.

## 3. Starter lint policy

Rust lints stay at `warn` so local builds keep working while CI promotes
warnings with `-D warnings`. Clippy lints only run under `cargo clippy`, so
hard rules can be `deny`.

```toml
[workspace.lints.rust]
unsafe_code = "deny"
missing_docs = "warn"
unreachable_pub = "warn"
unused_qualifications = "warn"
rust_2018_idioms = { level = "warn", priority = -1 }

[workspace.lints.clippy]
pedantic = { level = "warn", priority = -1 }
dbg_macro = "deny"
todo = "deny"
unimplemented = "deny"
unwrap_used = "deny"
expect_used = "deny"
panic = "deny"
allow_attributes_without_reason = "deny"
undocumented_unsafe_blocks = "deny"
multiple_unsafe_ops_per_block = "deny"
```

- Groups need a lower `priority` than individual lints so the individual
  levels win.
- `unsafe_code = "deny"` lets an approved module carry a scoped
  `#[expect(unsafe_code, reason = "...")]`; crates that never need `unsafe`
  add `#![forbid(unsafe_code)]` at the crate root.
- `pedantic` is optional. Enabling it means accepting targeted
  `#[expect(clippy::..., reason = "...")]` where a lint does not fit.
- Drop `missing_docs` for crates that expose no public API.
- Binary crates may add the allow-by-default `dead_code_pub_in_binary` lint
  (Rust 1.97) to catch unused `pub` items.

Allow test-only panics in `clippy.toml`. Clippy reads `rust-version` from the
manifest, so do not duplicate it as `msrv`. These keys cover `#[test]`
functions and anything under `#[cfg(test)]`, but not plain helper functions in
`tests/`; mark a shared helper module such as `tests/common/mod.rs` with
`#![cfg(test)]` and declare its helpers `pub(crate)` so `unreachable_pub` stays
quiet.

```toml
allow-unwrap-in-tests = true
allow-expect-in-tests = true
allow-panic-in-tests = true
allow-dbg-in-tests = true
```

## 4. Dependencies and supply chain

- Add dependencies with `cargo add` and check them with `cargo info`; never
  write crate names, versions, or features from memory (see
  `references/dependencies-release.md`).
- Commit `Cargo.lock` by default for libraries and binaries alike, as Cargo's
  guidance suggests; it makes CI and bisection reproducible. Libraries also
  need a CI job that runs after `cargo update` so the latest compatible
  dependency versions are exercised.
- Declare shared versions once in `[workspace.dependencies]`; disable default
  features when only a subset is needed.
- For a new `deny.toml`, start from `cargo deny init`, then set the license
  allowlist, deny unknown registries and git sources, set
  `advisories.unsound = "all"`, and add an empty `[bans.std-replacements]`
  table (cargo-deny 0.20+) to flag crates that std replaces.

## 5. CI baseline

Adapt package and feature selection to the repository; replace
`--all-features` with explicit rows or a feature powerset when features are
mutually exclusive.

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace --all-features
RUSTDOCFLAGS="-D warnings" cargo doc --workspace --no-deps --all-features
cargo hack check --workspace --rust-version
cargo hack check --workspace --feature-powerset --no-dev-deps
cargo deny check
```

Add a Miri job for crates that contain `unsafe` and `cargo semver-checks` for
published libraries. On Cargo 1.97 or newer, `CARGO_BUILD_WARNINGS=deny`
denies rustc, Clippy, and rustdoc warnings in one setting; older Cargo ignores
it, so keep `-D warnings` on MSRV rows. When the suite runs under nextest, keep
a separate `cargo test --doc` step because nextest does not run doctests.

## 6. Library documentation

- Write crate-level docs with `//!` in `lib.rs`, or reuse the README with
  `#![doc = include_str!("../README.md")]` so its examples run as doctests.
- For crates published to docs.rs, document every feature in
  `[package.metadata.docs.rs]` (for example `all-features = true`) so gated
  items appear. Add `#![cfg_attr(docsrs, feature(doc_cfg))]` for feature
  badges, never the removed `doc_auto_cfg`, and preview with
  `RUSTDOCFLAGS="--cfg docsrs" cargo +nightly doc`.
