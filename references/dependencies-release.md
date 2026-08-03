# Dependencies and release

Use this reference for dependency changes beyond the configured `cargo deny`
checks, and for verifying a crate intended for publication.

## 1. Dependency hygiene

Before adding or upgrading a dependency, answer proportionally to impact:

- why the dependency is necessary, and whether std or an existing dependency
  already suffices;
- which default features it activates, and whether
  `default-features = false` with explicit features is the better contract;
- whether its types appear in the public API, making its semver part of yours;
- whether the lockfile delta is larger than expected or introduces duplicate
  major versions of significant crates;
- whether its license, source, and provenance satisfy repository policy;
- whether it raises the effective MSRV of the package;
- whether a git or wildcard dependency is truly indispensable (approval rule in
  `SKILL.md`).

Run every configured `cargo deny` check and treat it as necessary evidence,
not sufficient proof of a sound dependency decision.

## 2. Publication verification

For a package intended for publication, validate the package artifact, not only
the workspace checkout:

- inspect the packaged file list (`cargo package --list`) for missing or
  accidental files;
- check metadata: description, license and readme paths, repository, keywords,
  and categories;
- confirm the docs.rs configuration and feature defaults produce the intended
  documentation;
- build the package as distributed (`cargo package` or
  `cargo publish --dry-run`) when practical;
- compare the public API against the latest published release with the
  compatibility review in `references/api-design.md`;
- confirm the changelog and version follow the repository's release
  convention.

A required release row that cannot run follows the unavailable-tool rules in
`references/workflow.md`.
