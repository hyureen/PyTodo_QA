# Automation candidates, regression suite and reflection (Week 6)

## 1. Candidate selection
Criteria: **repetition, stability, criticality, regression value**. Not automated: exploratory checks, visual/usability
judgement, accessibility judgement, one-off cross-browser checks on members' laptops.

| Layer (pyramid) | Tool | Tests |
| --- | --- | --- |
| UI / end-to-end (few) | Selenium + Page Object Model | 10 |
| API / integration | PyTest + Flask test client | 108 |
| Unit (many) | PyTest parametrize | 29 |

## 2. Regression suite
52 tests tagged `@pytest.mark.regression` (high-risk areas, frequently used features, critical
rules, every failed boundary). Failing ones are known defects and act as **confirmation tests** after a fix; the rest
check that the fix broke nothing.

## 3. Reflection
- **Benefits:** the non-UI suite runs in about 13 s, so it was re-run many times with identical results; documents are
  generated from results, keeping IDs consistent.
- **Limitations:** writing scripts took longer than one manual run; one Selenium test was flaky until waits and a
  retry were added; automation cannot judge usability or visual quality.
