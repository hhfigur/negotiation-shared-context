# Root-Cause Debugging Protocol

## Core rule

Do not patch from a plausible hypothesis. Diagnose first, fix second.

## Diagnosis sequence

1. Define observed and expected behavior precisely.
2. Establish environment, revision, inputs, timing, and impact.
3. Reproduce safely or explain why reproduction is blocked.
4. Capture raw logs, traces, test output, screenshots, state, or minimal examples without secrets.
5. Build a timeline and correlate relevant changes.
6. Enumerate competing hypotheses, including non-code causes.
7. Design discriminating tests that can reject hypotheses.
8. Execute read-only or non-destructive tests and record results.
9. State the causal chain, contributing conditions, detection gap, confidence, and residual uncertainty.
10. Define a regression test that distinguishes broken from fixed behavior.
11. Bound the smallest effective fix and obtain authorization.

## Evidence classes

- Direct: failing test, trace, state transition, query result, or source path demonstrating the mechanism.
- Corroborating: multiple independent observations consistent with the mechanism.
- Circumstantial: timing or correlation that narrows but does not prove the cause.
- Speculative: possible explanation without discriminating evidence.

Do not label speculative or merely correlated evidence as confirmed root cause.

## Fix sequence

1. Confirm the accepted diagnosis and authorized boundary.
2. Add or preserve the regression test.
3. Make the smallest effective change.
4. Run the regression test and adjacent non-regression checks.
5. Compare observed causal mechanism before and after.
6. Record deviations, evidence, residual uncertainty, and follow-up prevention or detection work.
