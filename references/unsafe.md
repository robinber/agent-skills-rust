# Unsafe and FFI

Use this reference whenever adding, reviewing, refactoring, or documenting
`unsafe` code, raw pointers, FFI, or safe abstractions over system interfaces.
When unsure, consult the Reference's
[behavior considered undefined](https://doc.rust-lang.org/reference/behavior-considered-undefined.html),
the [`std::ptr` safety documentation](https://doc.rust-lang.org/std/ptr/index.html),
and the [Rustonomicon](https://doc.rust-lang.org/nomicon/).

Contents: 1. Approval scope · 2. Rules · 3. Edition 2024 · 4. Soundness ·
5. FFI contract · 6. Verification

## 1. Approval scope

Introducing or widening `unsafe` needs explicit approval when repository policy
forbids it, when the task does not name an unsafe, FFI, or system boundary, or
when the change would reach beyond the named surface.

A task that explicitly names an FFI, raw-pointer, allocator, kernel, or
unsafe-abstraction surface approves the minimal set of entry points, types, and
unsafe operations it names or necessarily implies. `unsafe` outside that set,
such as helper allocators, general-purpose parsers, or unrelated modules, needs
its own approval. Approval never waives the rules below.

## 2. Rules

1. Use `unsafe` only when no adequate safe implementation exists. A
   performance motivation needs a measured comparison against a safe baseline.
2. Keep each `unsafe` block minimal; do checks and setup in safe code around it.
3. Give every `unsafe` block a `// SAFETY:` comment with the local proof: which
   pointers are valid, aligned, initialized, and non-aliasing; which lifetimes
   or ownership transfers justify the operation; which external contracts are
   assumed; why concurrent access is safe.
4. Document `# Safety` preconditions on every public `unsafe fn`. Mark a
   function `unsafe` only when misuse can cause undefined behavior, not merely
   because it is dangerous. An `unsafe impl` states which trait invariants hold
   and why safe callers cannot break them.
5. Expose a small safe API rather than raw unsafe operations.
6. Never use `static mut`; use atomics, `OnceLock`, or a lock.
7. Never round-trip pointers through integers with `as`. Manipulate pointer
   bits with `addr`, `with_addr`, and `map_addr` (1.84); use
   `expose_provenance` and `with_exposed_provenance` only for FFI or MMIO
   addresses.
8. Do not dilute a repository-wide `unsafe_code = "deny"` with local
   workarounds; encode an approved deviation at the smallest scope and in the
   documented repository contract.
9. Where `unsafe` is allowed, enable `clippy::undocumented_unsafe_blocks`,
   `clippy::multiple_unsafe_ops_per_block`, and, with a 1.99+ toolchain floor,
   the rustc lint `raw_borrows_via_references`.

```rust
pub fn ascii_prefix(bytes: &[u8]) -> &str {
    let end = bytes.iter().position(|b| !b.is_ascii()).unwrap_or(bytes.len());
    // SAFETY: every byte in `bytes[..end]` is ASCII (checked by `position`
    // above), and ASCII bytes are always valid UTF-8.
    unsafe { std::str::from_utf8_unchecked(&bytes[..end]) }
}
```

## 3. Edition 2024

- Unsafe operations inside an `unsafe fn` still need their own `unsafe` block
  (`unsafe_op_in_unsafe_fn` warns by default); prove each one locally.
- Extern blocks are written `unsafe extern`.
- `no_mangle`, `export_name`, and `link_section` are written
  `#[unsafe(...)]` and need a justification. Both forms work from Rust 1.82 in
  every edition.

## 4. Soundness

- Soundness is a module property. The proof must cover every function in the
  module that can modify the state the unsafe code relies on; keep that state
  private.
- Assume hostile safe callers. Never rely on caller-supplied safe trait
  implementations (`Ord`, `Eq`, `Hash`, `Clone`, `Deref`,
  `Iterator::size_hint`, `ExactSizeIterator::len`) for memory safety.
- Keep state valid before calling code that may panic, such as user closures
  or trait methods: set `len` only after elements are initialized, or use a
  drop guard.
- Error and early-return paths must leave no broken invariant, and drop paths
  must be sound. `ManuallyDrop`, raw ownership transfer, and custom
  deallocation need an exactly-once release proof (see
  `references/ownership-raii.md`).
- `unsafe impl Send` or `unsafe impl Sync` is new unsafe; see
  `references/concurrency.md`.

## 5. FFI contract

For every foreign boundary, record and verify:

- **ABI**: the correct `extern` ABI string, written `unsafe extern` on edition
  2024.
- **Layout**: every type crossing the boundary has a defined, ABI-compatible
  representation and a valid-value set matching the foreign contract.
  `repr(C)` does not repair non-FFI-safe nested fields; `repr(transparent)` is
  only as FFI-safe as its field. Keep `improper_ctypes` and
  `improper_ctypes_definitions` passing and match integer widths to the
  foreign declaration.
- **Validity**: which pointers may be null or dangling, and how long each must
  stay valid.
- **Strings and buffers**: length, encoding, and termination on both sides.
- **Ownership**: which side allocates and which frees, and the double-free and
  leak behavior of every error path.
- **Callbacks and unwinding**: threading, reentrancy, and context-pointer
  lifetime. Since Rust 1.81 a Rust panic escaping an `extern "C"` function
  aborts the process; use `catch_unwind` when an abort is unacceptable, and
  `extern "C-unwind"` when unwinding across the boundary is intended. Foreign
  exceptions unwinding into an `extern "C"` function remain undefined
  behavior.
- **Errors**: how foreign error codes or `errno` map to typed Rust errors.

Generated bindings and vendored stubs may contain bulk `unsafe`; isolate them
and document the trust boundary.

## 6. Verification

Test the safe abstraction's guarantees, including adversarial inputs and
panicking callbacks, and run Miri:

```bash
cargo +nightly miri test -p <package> <target-selection> <feature-selection> <test-filter>
```

- With threads or atomics, explore several schedules with
  `MIRIFLAGS="-Zmiri-many-seeds=0..16"`; one seed is one interleaving.
- For byte-order-sensitive code, also run Miri on a big-endian target
  (`--target s390x-unknown-linux-gnu`).
- Add `-Zmiri-strict-provenance` when code manipulates pointer bits. Never
  switch aliasing models (`-Zmiri-tree-borrows`) just to get a green run;
  report the finding.

When Miri cannot run (FFI, device I/O, unsupported syscalls), compensate with
focused safe-API tests, boundary assertions, sanitizers,
`cargo +nightly careful test`, and review of drop and error paths. On x86_64
Linux, stable sanitizer targets exist: `rustup target add
x86_64-unknown-linux-gnuasan` (also `gnumsan` and `gnutsan`), then test with
`--target`. Report the uncovered surface; never claim full dynamic safety
coverage.
