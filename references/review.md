# Code review

Use this reference for the "Code review" task class in `SKILL.md`. Discovery,
verification scoping, and completion states follow the core workflow; this file
defines the shape of the review itself.

## 1. Finding standard

A material finding must include:

- severity: critical, high, medium, or low;
- confidence: confirmed, likely, or uncertain;
- the exact affected location (file, item, and line where possible);
- the violated contract, invariant, or policy;
- a concrete failure scenario: which inputs or state produce which wrong
  outcome;
- the smallest reasonable remediation;
- the missing or insufficient test, when applicable.

Do not report a preference as a defect unless it violates repository policy,
Rust correctness, a documented contract, or creates a concrete maintenance
risk. Do not restate style already enforced by rustfmt or the configured lints.

## 2. Review passes

1. **Contract**: does the diff respect repository policy, public API
   compatibility, and documented invariants?
2. **Correctness**: error paths, panic surface, arithmetic and conversions,
   concurrency, and unsafe proofs, using the matching references.
3. **Tests**: would the included tests fail if the found defects were
   introduced? Name the uncovered behavior when they would not.
4. **Scope**: unrelated changes, accidental files, lockfile, feature,
   visibility, and suppression deltas.

Verify each suspected defect against the actual code and, when execution is
authorized, with the narrowest command that can confirm it. Keep confirmed
findings separate from unverified suspicions.

## 3. Output order

1. Material findings, highest severity first.
2. Open questions and unverified assumptions.
3. Verification performed and gaps.
4. Concise overall assessment.
5. For a non-trivial review, the mandatory completion schema from `SKILL.md`
   closes the report after the assessment.

When no material finding exists, state that explicitly and list the remaining
unverified risk surfaces. A review may report valid findings while stating that
checks were not executed; never imply executed verification that did not run.
