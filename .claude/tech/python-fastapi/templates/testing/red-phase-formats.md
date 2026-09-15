# RED Phase Formats — python-fastapi

## Test Disable Marker

- `@pytest.mark.skip(reason="RED: <predicted exception + message>")` on the failing test function/class.
- Add the marker ONLY after running the test unskipped and confirming the predicted failure (type + message/field) matches.

## Predicted Failure Types

| Situation | Predicted failure |
|-----------|-------------------|
| Method/route/attr does not exist yet | `AttributeError` / `NameError` / 404 |
| Real adapter stub | `NotImplementedError` (from `raise NotImplementedError()`) |
| Returns `None`/`[]`/`{}` placeholder | `AssertionError` on strict equality |
| Wrong enum/field value | `AssertionError` with the mismatched field |
| Domain rule not enforced | missing `pytest.raises(SomeDomainException)` |

## Prediction Verification (before accepting RED)

1. Run: `pytest path::TestClass::test_method` (unskipped).
2. Confirm the failure **type** matches the prediction.
3. Confirm the failure **message/field** matches (not just "it failed").
4. Only then add `@pytest.mark.skip` and commit the RED state.

## Commit

- RED commit includes the new (skipped) test and any minimal domain plumbing/stubs — never the real implementation.
