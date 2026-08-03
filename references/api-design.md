# api-design

## 1. Source-backed guidance

- Follow the
  [Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html).
- Naming: `snake_case` for functions/modules, `UpperCamelCase` for types/traits,
  conversion prefixes `as_` / `to_` / `into_`, getters without a useless `get_`
  prefix unless needed for disambiguation.
- Use common traits when they are semantically correct: `Debug`, `Display`,
  `Clone`, `Eq`, `Hash`, `Default`, and standard conversion traits (`From`,
  `TryFrom`, `AsRef`, `AsMut`).
- Prefer newtypes to encode meaningful distinctions, builders for many
  construction knobs, and `From`/`TryFrom` for explicit conversions.
- Avoid ambiguous `bool` parameters in public APIs when a named type or enum
  would communicate intent better.
- Keep public fields private when future layout changes should not break
  callers; expose accessors or constructors instead.
- For fallible construction, follow the crate's existing convention. Prefer
  `try_new` / `build` / `TryFrom` when that better distinguishes a fallible
  constructor from an infallible `new`; a fallible `new() -> Result<…>` is valid
  idiomatic Rust when that is the established API.
- Seal traits that are not meant for downstream implementation.

### Async public traits

Do not default to public `async fn` in traits without considering auto-traits
and object safety. Choose deliberately:

| Goal | Prefer |
|---|---|
| Multi-threaded executors | methods returning `impl Future<Output = T> + Send` (or equivalent) |
| Single-threaded / thread-local / some embedded | intentionally `!Send` futures; document the executor assumption |
| Both worlds | paired traits or `trait-variant`-style splits |
| Dynamic dispatch | object-safe design with boxed/pinned futures as needed |

Requiring `Send` forever is a public contract. Do not force it when the crate's
executor model is single-threaded.

## 2. Review checklist

Before exposing or changing a public item, confirm:

| Check | Question |
|---|---|
| Naming | Does it read like idiomatic Rust, with consistent word order? |
| Meaning | Would a newtype or enum remove a class of misuse? |
| Fallibility | Is failure visible in the type system when recoverable? |
| Traits | Is `Debug` present (and secret-safe)? Are `Send`/`Sync` intentional? |
| Errors | Is the error type meaningful, and are `Errors`/`Panics`/`Safety` documented? |
| Surface | Is this the smallest public surface that still supports the use case? |
| Stability | Would a private field or sealed trait preserve future flexibility? |
| Examples | Would a short rustdoc example prevent the most likely misuse? |

### Semver and compatibility

For a published library or a reusable workspace crate, review compatibility as
part of the public contract. Internal binaries may skip tooling that has no
meaningful downstream consumer, but should still review caller impact.

Check explicitly for:

- removed or renamed public items, reduced visibility, and changed signatures;
- public feature removal, renaming, default changes, or newly invalid feature
  combinations;
- trait method additions, object-safety changes, and downstream implementation
  breakage;
- changes to `Send`, `Sync`, `Unpin`, or other auto-trait behavior;
- stronger generic/lifetime bounds or changed associated types;
- variants added to publicly matchable error enums and other exhaustiveness
  hazards;
- dependency or API changes that raise the declared MSRV.

Use the repository's compatibility job when configured. Otherwise consider
[`cargo-semver-checks`](https://github.com/obi1kenobi/cargo-semver-checks) when
practical:

<!-- command-fixture: semver-check -->
```bash
cargo semver-checks --package <package>
```

An unavailable compatibility tool follows `references/workflow.md`; it does not
turn a manual review into a machine-verified compatibility claim.

## 3. Skill policy

- Make names read like Rust, not like a generic OO API.
- Expose types that carry meaning; do not encode domain states as loose
  primitives when a newtype or enum is clearer.
- Default to the smallest public surface that still supports the use case.
- Use a builder when construction has optional knobs, validation, or
  order-sensitive setup; use a simple `new` only when that truly stays simple.
- Write rustdoc for public entry points as if the example will be copied into
  another crate.
- Prefer validating at construction so the rest of the code can rely on
  invariants.
- In binaries and internal application crates, prefer `pub(crate)` unless the
  binary, integration tests, or a deliberate public surface needs the item
  public.
- For secret-bearing types, implement redacted `Debug`/`Display` or omit them
  rather than deriving full dumps.
- Preserve semver compatibility for published/reusable crates unless the exact
  break has explicit approval under `SKILL.md`.

## 4. Allowed exceptions

- Private helpers may use `bool`, ad hoc naming, or direct primitive parameters
  when the scope is local and the intent is obvious.
- Domain-specific constructor names like `open`, `bind`, or `connect` are fine
  when they match the resource being created.
- An internal binary can stay binary-only if it is not meant to be reused or
  depended on as a library.
- Skip a builder or newtype when it adds ceremony without meaningful clarity or
  validation benefit.
