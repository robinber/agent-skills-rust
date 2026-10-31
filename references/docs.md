# Documentation

## 1. What to document

- Document every public crate, module, type, function, trait, and method meant
  for others. Under `missing_docs`, a short non-repetitive sentence is enough
  for obvious items.
- Start with a one-line summary of about 15 words, then explain the contract:
  what it is for, how to use it, and the caveats that affect callers. Explain
  parameters in prose; do not add `# Arguments`, `# Parameters`, or `# Returns`
  sections.
- Add `# Errors`, `# Panics`, and `# Safety` sections whenever the item can
  fail, panic, or carries unsafe preconditions.
- Document the end state only. No design journals, "we chose X over Y",
  "previously...", or guideline-compliance notes in rustdoc, READMEs, or
  comments.
- Comment private code only where the reason is not obvious from the code.
  Generated code and internal organizing modules need little documentation.

## 2. Examples

- Write examples as if they will be copied into another crate: short, runnable,
  and showing the behavior the reader needs. Hide only compile scaffolding.
- Use `?` in examples, with a hidden `fn main() -> Result<...>` or a trailing
  `# Ok::<(), Error>(())`, never `.unwrap()`.
- Doctests are part of the correctness surface. A rustdoc build does not run
  them; run `cargo test --doc` when runnable examples change.

## 3. Gates

Use the scoped rustdoc command in `references/workflow.md` when public docs
change. Under `RUSTDOCFLAGS="-D warnings"` (not `RUSTFLAGS`), broken intra-doc
links, bare URLs, and links from public docs to private items
(`rustdoc::private_intra_doc_links`, warn-by-default) fail the build. Verify
both rustdoc and doctests before finalizing public documentation changes
unless the repository documents a different split.
