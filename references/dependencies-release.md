# Dependencies and release

Use this reference when adding, upgrading, or removing dependencies, changing
`deny.toml`, or verifying a crate intended for publication.

Contents: 1. Choosing and adding · 2. Resolution and lockfile · 3. Advisory
checks · 4. Publication

## 1. Choosing and adding

- Never write a crate name, version, feature, or API from memory: hallucinated
  names get registered by attackers, and major versions rename APIs. Add
  dependencies with `cargo add <name>[@<version>] -F <features>`.
- Read the full `cargo info <name>` output (Cargo 1.82+): a `+deprecated`
  version suffix, the README, the features, and `rust-version`. `cargo add`
  does not warn about deprecated or tombstone releases.
- Check RustSec even when the repository configures nothing
  (`cargo deny check advisories` or `cargo audit`). Do not silently add or pin
  a crate flagged unmaintained, unsound, or deprecated; report it.
- Write calls against the documentation of the resolved version. When it is a
  newer major version than you know, read the breaking section of its
  changelog first.

Before adding or upgrading, answer proportionally to impact:

- why the dependency is necessary, and whether std or an existing dependency
  already suffices;
- which default features it activates, and whether `default-features = false`
  with explicit features is the better contract;
- whether its types appear in the public API, making its semver part of yours;
- whether the lockfile delta is larger than expected or duplicates major
  versions of significant crates (`cargo tree -d --target all`;
  `cargo tree -i <crate> -e features` shows who enables what);
- whether its license, source, and provenance satisfy repository policy;
- whether it raises the effective MSRV;
- whether a git or wildcard dependency is truly indispensable (approval rule in
  `SKILL.md`).

## 2. Resolution and lockfile

- Never run a bare `cargo update` inside a change; update only what the change
  needs with `cargo update -p <crate> --precise <version>`.
- Resolve within the declared MSRV: `resolver = "3"` (edition 2024 default) or
  `resolver.incompatible-rust-versions = "fallback"` makes Cargo 1.84+ prefer
  dependency versions compatible with `rust-version`.
- Keep version requirements honest. A lockfile can hide that `"1.0"` actually
  needs a later 1.x API; published libraries can check lower bounds with
  `cargo +nightly update -Zdirect-minimal-versions` followed by a build.
- Respect a configured dependency cooldown (`registry.global-min-publish-age`
  or `registries.<name>.min-publish-age`, Cargo 1.100): the resolver ignores
  versions published inside the window unless `Cargo.lock` already holds them.
  Without approval, never reach a fresher version by lowering the age, setting
  `resolver.incompatible-publish-age = "allow"`, editing `Cargo.lock` by hand,
  or switching to a git source. When the only fix for an advisory is still
  inside the window, report it and let the user decide (approval rule in
  `SKILL.md`). An approved bypass covers one command and leaves the
  configuration unchanged:
  `CARGO_RESOLVER_INCOMPATIBLE_PUBLISH_AGE=allow cargo update -p <crate> --precise <version>`.
- A repository without a cooldown is a candidate for the setup in
  `references/project-setup.md`; suggest it rather than adding it unasked.
  Never present a cooldown as proof that a dependency is safe: older Cargo
  ignores it, and it does not cover versions without a recorded publish time
  or git, path, and vendored sources.
- Remove dependencies that are no longer used. On Cargo 1.100 or newer the
  built-in `cargo::unused_dependencies` lint is the first signal, because it
  comes from the build itself rather than from a scan of the source. It
  covers `[dependencies]` and `[build-dependencies]` of the selected packages
  only, so keep `cargo machete`, `cargo shear`, or the
  `unused_crate_dependencies` lint for `[dev-dependencies]` and for older
  Cargo. Before removing a flagged dependency, check every feature and target
  row: one used only behind a feature or a `cfg` becomes optional or
  target-specific instead, and one listed only to enable a feature or pin the
  version of a transitive dependency is a documented false positive (for a
  pin, Cargo's documentation suggests moving it under
  `[target."cfg(false)".dependencies]`).

## 3. Advisory checks

Run every configured supply-chain gate (`cargo deny`, cargo-vet's
`supply-chain/`, cargo-audit configuration) and treat it as necessary
evidence, not proof of a sound dependency decision. Do not overstate coverage:
cargo-deny ignores `unsound` advisories in transitive dependencies unless
`advisories.unsound = "all"`, and `cargo audit` only warns about unsound,
unmaintained, and yanked crates unless run with `-D`.

## 4. Publication

For a package intended for publication, validate the package artifact, not only
the workspace checkout:

- inspect the packaged file list (`cargo package --list`) for missing or
  accidental files;
- check metadata: description, license and readme paths, repository, keywords,
  and categories;
- confirm the docs.rs configuration and feature defaults produce the intended
  documentation (see `references/project-setup.md`);
- build the package as distributed with `cargo package` or
  `cargo publish --dry-run`; when crates depend on unpublished siblings, use
  `cargo package --workspace` or `cargo publish --workspace --dry-run`
  (multi-package publishing is not atomic);
- compare the public API against the latest published release with the
  compatibility review in `references/api-design.md`;
- confirm the changelog and version follow the repository's release
  convention.

Publish from CI with crates.io trusted publishing
(`rust-lang/crates-io-auth-action`), granting `id-token: write` to the publish
job only, instead of a long-lived token secret. The first publish of a crate is
still manual.

A required release row that cannot run follows the unavailable-tool rules in
`references/workflow.md`.
