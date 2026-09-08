# Milestone report template

Every milestone report in `reports/milestones/` uses these 15 fields, in this
order, numbered and titled exactly as below. A field that cannot be completed
reads **PENDING --- <who/what it awaits>** and names the exact evidence
expected. No field is deleted, and none is answered with "n/a" where evidence
is simply missing.

---

## 1. Milestone ID and title

## 2. Objective
What this milestone was meant to achieve, and what it explicitly excluded.

## 3. Repository commit SHA
The commit the work is pinned to, and the state of the remote.

## 4. Data version and checksums
Every data file touched: SHA-256, byte size, shape, and storage policy.

## 5. Environment and execution location
Every environment the work ran in: kind, Python version, platform, dependency
fingerprint, and the location label recorded in run records.

## 6. Work completed
What was actually done, in enough detail to repeat it.

## 7. Deliverables and exact file paths
Every file produced, by repo-relative path.

## 8. Methods and rules that affect scientific meaning
Any rule applied that changes what the data means: filtering, aggregation,
unit conversion, type coercion, renaming, imputation, exclusion. If none was
applied, say so plainly --- this field is never left blank.

## 9. Results with compact tables or examples
The findings themselves, as tables or short examples rather than prose.

## 10. Validation performed
Which checks were run and their results: tests, scans, smoke tests,
cross-host verification.

## 11. Failures, rejected cases, and known limitations
What broke, what was tried and rejected, and what remains weak. Stating a
limitation here is not an admission of failure; hiding one is.

## 12. Deviations from the approved plan
Anything done differently from the issued work package, and why.

## 13. Open decisions and mentor questions
What is unresolved, who owns it, and what it blocks.

## 14. Proposed gate status
Each gate criterion from `docs/PROJECT_PLAN.md`, quoted verbatim, with
MET / NOT MET / PENDING and the evidence for that judgement. Then a single
proposed status for the milestone as a whole.

## 15. Proposed next bounded objective
One objective, scoped tightly enough to be executed as a single work package.
Not a list of actions.
