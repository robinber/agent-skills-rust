# unsafe

Use this reference whenever adding, reviewing, refactoring, or documenting
`unsafe` code, raw pointers, FFI, or safe abstractions over kernel/system
interfaces.

## 1. Source-backed guidance

- Prefer safe Rust first. `unsafe` is a boundary where the compiler stops proving
  memory safety; the author must prove it instead.
- Read the [Rustonomicon](https://doc.rust-lang.org/nomicon/) and the
  [Unsafe Code Guidelines](https://rust-lang.github.io/unsafe-code-guidelines/)
  when unsure.
- Standard library policy: each `unsafe` block should have a `SAFETY` comment
  explaining why the block is sound and which invariants must hold. See the
  [safety comments policy](https://std-dev-guide.rust-lang.org/policy/safety-comments.html).
- Public `unsafe fn` items need a rustdoc `# Safety` section describing caller
  obligations.
- `unsafe impl` of unsafe traits needs the same quality of local proof: which
  invariants of the trait are upheld and why callers cannot break them via the
  safe API.
- Safe wrappers should encapsulate invariants so ordinary callers cannot cause
  undefined behavior.

## 2. Edition 2024 checklist

When the crate edition is 2024 (or newer), also confirm:

- **`unsafe_op_in_unsafe_fn`**: unsafe operations inside `unsafe fn` still need
  an `unsafe` block (or an explicit opt-out with justification). Do not assume
  the function body is an implicit unsafe region.
- **`unsafe extern`**: extern blocks use the edition's `unsafe extern` form when
  required; document the FFI contract.
- **`#[unsafe(...)]` attributes**: items such as `no_mangle` / link attributes
  that the edition treats as unsafe must use the `#[unsafe(...)]` form and stay
  justified.
- Keep proofs local: a SAFETY comment on an outer function is not a substitute
  for proofs on each unsafe operation when the edition requires explicit blocks.

See the
[Edition Guide on unsafe ops in unsafe fn](https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-op-in-unsafe-fn.html)
and the
[Reference on `unsafe`](https://doc.rust-lang.org/reference/unsafe-keyword.html).

## 3. Skill policy

Hard rules:

1. Do not introduce `unsafe` unless the slice requires it and no safe API is
   adequate.
2. Keep `unsafe` blocks as small as possible. Push checks and setup into safe
   code around them.
3. Every `unsafe` block must include a `// SAFETY:` comment that states the local
   proof, not a vague claim that "this is fine".
4. Every public `unsafe fn` must document `# Safety` preconditions.
5. Prefer a small safe API over exporting raw unsafe operations.
6. Do not dilute repo-wide `unsafe_code = "deny"` casually. If the package must
   use `unsafe`, relax the lint at the smallest module or item scope with a
   justified reason, or adopt an explicit package policy documented in
   `AGENTS.md`.
7. Prefer mechanical enforcement: enable `clippy::undocumented_unsafe_blocks`
   and `clippy::multiple_unsafe_ops_per_block` when the package allows `unsafe`.
8. When changing `unsafe`, add or update tests for the safe abstraction's
   guarantees. Prefer:

```bash
# When the logic is Miri-compatible (pure memory / no unsupported syscalls):
cargo +nightly miri test -p <package> -- <test-filter>

# When Miri cannot run (device I/O, io_uring, many syscalls), compensate:
# - focused safe-API tests and adversarial edge cases
# - boundary assertions
# - sanitizers when practical (`-Zsanitizer=address`, or `cargo careful` if available)
# - careful review of drop/error paths
```

### Good SAFETY comments

State:

- which pointers/handles are valid, aligned, initialized, and non-aliasing as
  required;
- which lifetimes or ownership transfers justify the operation;
- which external contracts (kernel, FFI, hardware) are assumed;
- why concurrent access is safe if shared state is involved.

### Safe abstraction checklist

| Question | Expected answer |
|---|---|
| What invariant does the safe type maintain? | Documented on the type |
| Can a safe caller break that invariant? | No |
| Is the `unsafe` region minimal? | Yes |
| Are error and early-return paths free of UB and left-behind broken invariants? | Yes |
| Are drop/cleanup paths sound? | Yes |

## 4. Allowed exceptions

- Generated bindings and vendor stubs may contain bulk `unsafe`; still isolate
  them and document the trust boundary.
- Performance-motivated `unsafe` needs a measured reason and a safe baseline
  comparison when practical; "might be faster" is not enough.
- If neither Miri nor sanitizers can cover the path, document the gap explicitly
  and do not claim full dynamic safety coverage.
