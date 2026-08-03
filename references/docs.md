# docs

## 1. Source-backed guidance

- Rustdoc emphasizes documenting public items, examples, and the API contract
  visible to users. See the rustdoc book on
  [how to write documentation](https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html).
- Public-facing items should explain what they are for, how to use them, and the
  important caveats that affect callers.
- Examples should be short, runnable, and representative. If an example needs
  setup noise, hide only the unhelpful scaffolding, not the behavior the reader
  needs to see.
- For APIs that can panic, fail, or rely on unsafe assumptions, document
  `Panics`, `Errors`, and `Safety` sections where they apply.
- Rustdoc tests compile the examples you show, so docs are part of the
  correctness surface, not just prose.

## 2. Rustdoc and doctest gates

When repository policy requires `RUSTDOCFLAGS="-D warnings"`, verify docs with:

```bash
RUSTDOCFLAGS="-D warnings" cargo doc -p <package> --no-deps <features-or-default>
```

In a workspace, use `--workspace` or package selection as appropriate. Under
that flag:

- Broken intra-doc links are build failures.
- Bare URLs and other rustdoc warnings are build failures.
- Private intra-doc links (`rustdoc::private_intra_doc_links`) are
  warn-by-default, so they fail the build under `-D warnings` without extra
  package configuration.

`cargo doc` does **not** run doctests. When runnable rustdoc examples change,
also run:

```bash
cargo test -p <package> --doc <features-or-default>
```

When public docs or rustdoc examples change, verify locally with both gates
before finalizing (unless the repo documents a different split).

## 3. Skill policy

- Document every public crate, module, type, function, trait, and method that is
  meant to be consumed by others.
- Keep docs focused on the contract, not an internal tour of the implementation.
- Explain examples in the same terms a caller would use, and prefer one good
  example over many weak ones.
- Make `Panics`, `Errors`, and `Safety` sections explicit when the API can
  trigger them; do not bury those details in prose.
- For private helpers and trivial internal glue, write only the comments needed
  to keep the code readable.
- When `missing_docs` is denied, every public item needs at least a short doc; a
  brief non-repetitive sentence is enough for obvious getters.

## 4. Allowed exceptions

- Trivial private code, generated code, and one-line helpers do not need
  exhaustive documentation.
- Internal modules that exist only to organize implementation details can stay
  lightly documented if they are not part of the API surface.
- Omitting public docs is allowed only when the repository's lint policy permits
  it. Prefer a short doc over silence under `missing_docs = "deny"`.
- If a doc example would be misleading because it omits essential setup, keep
  the example minimal and hide only the boilerplate needed for compilation.
