# Idiomatic and modern Rust

Use this reference when writing, restructuring, or porting Rust code. It lists
the idioms coding agents most often get wrong; it does not restate the
language.

Contents: 1. Modern std over legacy crates · 2. Ownership in signatures ·
3. Types and control flow · 4. Porting from other languages · 5. Performance

## 1. Modern std over legacy crates

Use the std facility when the declared `rust-version` allows it, and never use
an API or syntax newer than that MSRV. Clippy's `incompatible_msrv` flags
too-new library items but not syntax. Modernize code you touch, not unrelated
code.

| Instead of | Prefer | Since |
|---|---|---|
| `lazy_static!`, `once_cell::sync::Lazy` | `std::sync::LazyLock` | 1.80 |
| `once_cell::sync::OnceCell` with infallible init (`get_or_try_init` is unstable) | `std::sync::OnceLock` | 1.70 |
| `once_cell::unsync::Lazy` | `std::cell::LazyCell` | 1.80 |
| `atty` | `std::io::IsTerminal` | 1.70 |
| `crossbeam::scope` | `std::thread::scope` | 1.63 |
| `num_cpus::get` (logical CPU count only) | `std::thread::available_parallelism` | 1.59 |
| `memoffset` | `std::mem::offset_of!` | 1.77 |
| `home`, `dirs::home_dir` for the home directory only | `std::env::home_dir` | 1.87 |
| `as_any()` / `as_super()` helper methods | trait upcasting (`&dyn Sub` to `&dyn Super`) | 1.86 |
| `unwrap()` on `Result<T, Infallible>` | `let Ok(v) = result;` | 1.82 |
| parsing or unwrapping inside an arm after a guard | `if let` guards (`Some(s) if let Ok(n) = s.parse() =>`) | 1.95 |
| `retain` plus clones or index loops to remove and collect | `extract_if` | 1.87 |
| `Atomic*::fetch_update` (deprecated in 1.99) | `try_update`, or `update` when the closure cannot fail | 1.95 |
| `parking_lot::Mutex` chosen only for speed | `std::sync::Mutex` (futex-based) | 1.62 |
| `crossbeam-channel` with a single consumer | `std::sync::mpsc` | 1.67 |
| `async-trait` with static dispatch only | native `async fn` in traits | 1.75 |
| `F: Fn() -> Fut` bounds, unless the future must be `Send` (that needs unstable return type notation) | async closures and `AsyncFn*` bounds | 1.85 |
| `ptr::addr_of!` | `&raw const`, `&raw mut` | 1.82 |
| the `Captures` lifetime trick | `use<..>` precise capturing | 1.82 |
| `match` that only binds or returns early | `let ... else` | 1.65 |
| nested `if let` | let chains (edition 2024) | 1.88 |
| `#[allow(lint)]` plus a comment | `#[expect(lint, reason = "...")]` | 1.81 |
| `std::error::Error` in `no_std` code | `core::error::Error` | 1.81 |
| `os_pipe` | `std::io::pipe` | 1.87 |
| `fs2` / `fs4` file locks | `File::lock`, `File::try_lock` | 1.89 |
| `cfg-if` | `cfg_select!` | 1.95 |
| `assert!(matches!(..))` | `assert_matches!` (not in the prelude: `use std::assert_matches;`) | 1.96 |
| `structopt` | `clap` with derive | — |

Keep `async-trait` or boxed futures when the trait must be usable as
`dyn Trait`. Native `async fn` in a public trait does not promise `Send`; see
`references/api-design.md`.

## 2. Ownership in signatures

- Borrow what you only read (`&str`, `&[T]`, `&Path`); take ownership of what
  you store (`String`, `Vec<T>`, `PathBuf`). Use `impl Into<String>` or
  `impl AsRef<Path>` for ergonomic constructors, not on every function.
- Return `&str` or `&[T]` rather than `&String` or `&Vec<T>`.
- Do not `clone()` to silence the borrow checker. Shorten the borrow, borrow
  disjoint fields separately, use `std::mem::take` or `replace`, the entry API,
  `get_disjoint_mut` (1.86), or indices. A clone is fine when the value is
  cheap or truly needs a second owner.
- Use `Rc` and `Arc` for real shared ownership, not as a borrow-checker escape.
- Prefer `&mut self` over interior mutability (`Cell`, `RefCell`, `Mutex`)
  unless the value is genuinely shared.
- Use `Cow<'_, str>` when a function usually borrows but sometimes allocates.

## 3. Types and control flow

- Match exhaustively on enums you own and avoid `_ =>` arms, so a new variant
  fails to compile at every decision point. Reserve `_` for foreign
  `#[non_exhaustive]` types or genuinely uniform cases.
- Model states as enums carrying their data, not as combinations of `bool` and
  `Option` fields that permit invalid states.
- Use iterator adaptors for transformations and a `for` loop when the body has
  side effects, complex early exits, or many `?` steps. Do not `collect()` into
  a temporary `Vec` only to iterate it again.
- Implement `From` only for lossless, infallible conversions and `TryFrom` for
  fallible ones. Never write a `From` that panics or silently truncates.
- Provide `Default` (derived when possible) when `new()` takes no arguments.
- Mark functions whose return value is the point (pure computations, builder
  methods returning `Self`, guard constructors) `#[must_use]`.
- Call `std::process::exit` only from `main`; it skips destructors.

## 4. Porting from other languages

Translate the design, not the syntax:

- Model data and its owner first; do not reproduce class hierarchies.
- Avoid `Manager`, `Service`, `Factory`, and `Helper` types that exist only to
  hold functions; use modules, free functions, and types named for what they
  are.
- Do not create a trait per struct with `Arc<dyn Trait>` just for mocking.
  Start concrete, move to generics when a second implementation exists, and use
  `dyn` when heterogeneity or code size requires it.
- Do not implement `Deref` to simulate inheritance; `Deref` is for smart
  pointers.
- Keep `Arc<Mutex<T>>`, `Rc<RefCell<T>>`, and `Box<T>` out of public
  signatures; expose an owning type with methods instead.
- Replace exceptions with `Result`, null with `Option`, and runtime type checks
  with enums.

## 5. Performance

- Write correct, clear code first; optimize only with a measurement in the
  release profile (a benchmark harness or a profiler).
- Avoid accidental allocation on hot paths: `Vec::with_capacity` when the size
  is known, reused buffers, `write!` into an existing `String` instead of
  repeated `format!`.
- Prefer static dispatch on hot paths; use `dyn Trait` where heterogeneity or
  code size matters more.
- Add `#[inline]` only to small cross-crate functions with a measured benefit.
- Treat profile settings (`lto`, `codegen-units`, `panic = "abort"`) as
  deliberate repository choices; `panic = "abort"` changes cleanup guarantees
  (see `references/ownership-raii.md`).
- Never claim a speedup you did not measure.
