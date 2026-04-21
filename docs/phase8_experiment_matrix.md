# Phase 8 Experiment Matrix

## Purpose

Define the smallest executable validation matrix for `adapt010`.

This matrix is intentionally narrow. Its purpose is not to explore the adaptive space broadly, but to decide whether `adapt010` has enough repeatable value to remain the current adaptive candidate.

---

## Experiment Categories

## 1. Difficult-Case Repeatability Validation

### Intended experiment

Run a matched difficult-case rerun centered on the previously positive `adapt010` signal.

### What it is trying to prove

That the difficult-case gain is reproducible and not dependent on a single isolated favorable outcome.

### Supportive evidence

- `adapt010` again shows favorable direction on the difficult case
- the result remains interpretable under matched comparison
- the advantage is stable enough to justify keeping `adapt010` under validation

### Non-supportive evidence

- the gain disappears on rerun
- the direction becomes inconsistent or ambiguous
- the result only looks favorable under one narrow setup

---

## 2. Favorable-Case Guardrail Reinforcement

### Intended experiment

Run one conservative favorable-case check for `adapt010` under the same Phase 8 discipline.

### What it is trying to prove

That `adapt010` does not introduce unacceptable regression while pursuing difficult-case benefit.

### Supportive evidence

- favorable-case behavior remains acceptable
- no clear new regression appears
- the guardrail result is consistent with the earlier acceptable check

### Non-supportive evidence

- a clear favorable-case regression appears
- repeated checking reveals instability that was hidden before
- `adapt010` requires favorable-case sacrifice to preserve its difficult-case claim

---

## 3. Minimal Comparison Against Static Reference (`Phase 3.3 af025`)

### Intended experiment

Use the difficult-case and favorable-case checks above to produce one explicit side-by-side interpretation against `Phase 3.3 af025`.

### What it is trying to prove

That `adapt010` has a specific and defensible role relative to the current static reference.

### Supportive evidence

- `adapt010` shows repeatable difficult-case value that `af025` does not clearly match
- `adapt010` keeps favorable-case behavior within acceptable limits
- the trade-off can be stated clearly: selective difficult-case advantage in exchange for no unacceptable guardrail loss

### Non-supportive evidence

- `af025` remains clearly stronger once matched checks are rerun
- `adapt010` has no stable advantage beyond isolated results
- the comparison cannot be explained clearly without overfitting the interpretation

---

## Priority Order

## First Runs

- one matched difficult-case repeatability rerun for `adapt010`
- one favorable-case guardrail rerun for `adapt010`
- one short side-by-side interpretation against `Phase 3.3 af025` using those two checks

These runs are the minimum executable Phase 8 matrix.

## Optional Second Runs

- one additional difficult-case rerun if the first rerun is promising but not decisive
- one additional favorable-case check if the first guardrail result is acceptable but unusually close

These should only be added if the first runs leave the decision genuinely unresolved.

## What Should Not Be Run Yet

- broad seed sweeps
- new adaptive strengths beyond `adapt010`
- renewed exploration of `adapt025`
- architecture changes
- unrestricted multi-case expansion
- optimization-focused reruns intended to improve headline numbers

These should be deferred until `adapt010` first shows narrow, repeatable, decision-grade evidence.

---

## Immediate Batch Decision Rule

The matrix supports continuation only if all of the following are true:

- the difficult-case rerun is supportive
- the favorable-case guardrail rerun is supportive
- the comparison against `Phase 3.3 af025` yields a clear and defensible narrative

If one of these fails, the evidence is non-supportive or incomplete, and Phase 8 should either stop at one more narrow check or pause the adaptive direction.
