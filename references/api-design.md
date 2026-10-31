# API design

Contents: 1. Shape · 2. Cargo features · 3. Async traits and auto traits ·
4. Semver and compatibility · 5. Restraint

Follow the
[Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html);
the rules below are the ones most often missed.

## 1. Shape

- Expose the smallest surface that supports the use case. In binaries and
  application crates, default to `pub(crate)`.
- Give each public item one public path. After moving an item, do not leave a
  `pub use` alias behind, and never `pub use module::*`.
- Encode meaning in types: newtypes for distinct quantities and identifiers,
  enums for policy choices instead of `bool` parameters whose meaning is
  invisible at the call site.
- Keep fields private when future layout changes should not break callers;
  expose constructors and accessors.
- Validate at construction (see `references/correctness-safety.md`). For
  fallible construction, follow the crate convention: `try_new`, `build`, or
  `TryFrom` when the crate distinguishes them from an infallible `new`; a
  fallible `new() -> Result<...>` or a domain name such as `open`, `bind`, or
  `connect` is fine when established.
- Use a builder when construction has optional knobs, validation, or
  order-sensitive setup.
- Put trait bounds on the `impl` blocks that need them, not on the type
  definition; `struct Cache<K: Hash>` spreads the bound to every use and makes
  relaxing it a breaking change.
- Implement common traits when semantically correct (`Debug`, `Clone`, `Eq`,
  `Hash`, `Default`, `From`, `AsRef`). Every public type should implement
  `Debug`; for secret-bearing types, write a redacting `Debug` instead of
  deriving it.
- Mark public enums and structs expected to grow `#[non_exhaustive]` in
  published or reused crates. Downstream code must then add a wildcard arm and
  cannot use struct literals, so pair such structs with a constructor or
  builder. Leave closed sets, such as protocol states that callers must match
  exhaustively, exhaustive.
- Seal traits that downstream crates should not implement.
- Accept ranges in public APIs as `impl RangeBounds<T>` rather than a concrete
  `std::ops::Range<T>`; new range types are planned and this signature stays
  compatible.

## 2. Cargo features

- Keep features additive. Enabling a feature may add items or capabilities; it
  must not remove items, change existing behavior incompatibly, or break code
  that compiles without it. Cargo unifies features across the dependency graph,
  so any dependent can enable them.
- Gate standard-library support behind a default `std` feature, never behind a
  `no_std` feature.
- Avoid mutually exclusive features; prefer runtime configuration, a trait, or
  separate crates. When exclusivity is unavoidable, fail with `compile_error!`
  naming the conflicting features and document the valid combinations.
- Use `dep:` for optional dependencies so they do not become implicit features,
  and weak `?` forwarding (`"serde?/std"`) so a feature does not force an
  optional dependency on.
- Put test fakes and hooks needed by integration tests behind a non-default
  `test-util` feature instead of making them unconditionally public.
- Feature names and defaults are public API; see section 4.

## 3. Async traits and auto traits

A bare `async fn` in a public trait does not let callers require a `Send`
future, and rustc warns about it (`async_fn_in_trait`). Choose deliberately:

| Goal | Prefer |
|---|---|
| Multi-threaded executors | methods returning `impl Future<Output = T> + Send` |
| Single-threaded or embedded executors | `!Send` futures, with the executor assumption documented |
| Both | a `Send` variant generated with `trait_variant::make` |
| Dynamic dispatch | an object-safe design with boxed futures |

`Send`, `Sync`, and `Unpin` are public contracts. An `Rc` or a non-`Send` guard
held across `.await` silently makes a future `!Send`, and only downstream code
fails. Pin the contract with compile-time assertions for key public types and
for the futures of key public `async fn`s:

```rust
const _: () = {
    const fn assert_send_sync<T: Send + Sync>() {}
    assert_send_sync::<Client>();
};

#[test]
fn fetch_future_is_send() {
    fn assert_send<T: Send>(_: &T) {}
    let client = Client::default();
    assert_send(&client.fetch("key"));
}
```

## 4. Semver and compatibility

Review compatibility for published libraries and reused workspace crates. For
internal binaries, review caller impact without semver tooling. Check for:

- removed or renamed public items, reduced visibility, changed signatures;
- removed or renamed features, changed defaults, newly invalid combinations;
- trait method additions, object-safety changes, downstream impl breakage;
- auto-trait changes (`Send`, `Sync`, `Unpin`);
- stronger generic or lifetime bounds, changed associated types;
- variants added to exhaustive public enums; `#[non_exhaustive]` added or
  removed;
- `repr`, layout, or ABI changes callers may rely on;
- dependency types re-exported or embedded in the public API;
- macro output and resolution visible downstream;
- new inherent methods or blanket impls that change method resolution;
- changes that raise the declared MSRV.

The Cargo Book's SemVer chapter is the authoritative list. Use the repository's
compatibility job when configured, otherwise `cargo semver-checks` when
practical:

```bash
cargo semver-checks --package <package>
```

Its pass is supporting evidence, not proof that semantic, layout, macro, or
feature concerns are covered. Breaking a published or reused API needs explicit
approval (see `SKILL.md`).

## 5. Restraint

- Prefer the smallest coherent change that preserves correct local design.
- Do not introduce a trait, generic parameter, builder, dependency, feature, or
  crate for hypothetical reuse. Abstract stable shared knowledge or a real
  boundary, not similar-looking syntax.
- Private helpers may use `bool` or primitive parameters when the scope is
  local and the intent obvious.
- Keep unrelated cleanup out of the patch unless the requested change needs it
  to be safe and understandable.
