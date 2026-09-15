# Scan — Cluster T: Duplication & surface (structural + judgment)

Part of the refactor scan, run by `refactor-duplication-agent`. Hub + cluster
routing + output format: `scan-checklist.md`. Fix templates: `code-smells-routing-table.md`.

Two modes below. **Section A (structural):** produce numeric/objective data.
**Section B (judgment):** read the code, answer the question, and **cite the
snippet as evidence** or write "none found" — no bare "clean."
Skip checks marked with a file-type tag that doesn't match the target file.
The A46/A47/A57 here are the **frontend** rows (`.tsx` only) — the backend rows
of the same numbers belong to cluster D.

## Section A — Structural

**Sibling duplication** (any class extending a base or implementing same interface):

| # | Check | Enumerate | Violation |
|---|-------|-----------|-----------|
| A14 | Sibling duplication | Fields and methods appearing in 2+ sibling classes — read ALL siblings | Same member in 2+ siblings |

**Cross-class duplication** (not siblings — structurally identical but unrelated classes):

| # | Check | Enumerate | Violation |
|---|-------|-----------|-----------|
| A22 | Structurally identical classes | For each Fake or port interface, grep for other classes with identical method signatures and field structures. Example: `FakeTaskCreatedNotificationSender` and `FakeTaskMovedNotificationSender` both have `List<String> sentEmails` + `void send(String)`. | 2+ classes with identical structure → extract base class |
| A52 | Manual per-field assertion | Methods with 2+ sequential `assertThat(actual.fieldX())` lines reading **state fields off the same actual object** — whether the expected values come from one expected object, scattered constants/captured ids, or a mix, **and even when behavioral-predicate assertions** (`assertThat(actual.computedBoolean()).isTrue()`) are interleaved between them. Also `assertAllFields`-style helpers. The shape to catch is "a run of per-field reads on one object", NOT only the two-objects-side-by-side helper. List the method name and field count. Classify each field: exact-match, non-deterministic (isNotNull/isNotEmpty), null-check, or custom (timestamp truncation, range); and note whether the actual object has a **natural sibling expected in scope** (e.g., the just-saved entity returned by setup). | **Sibling expected in scope** (just-saved entity, captured before the round-trip) → collapse the state-field assertions into `assertThat(actual).usingRecursiveComparison().isEqualTo(sibling)`, adding `.ignoringFields(...)` only for fields that legitimately differ in the round-trip; keep interleaved behavioral-predicate assertions (calls to derived/computed methods, not field getters) separate — they assert derived behavior, not state. All fields exact-match against one expected → `usingRecursiveComparison().isEqualTo(expected)`. Mixed strategies (some non-deterministic/null/custom) → extract reusable assertion helpers as private methods (HTTP status, timestamp, error structure), keep field-specific assertions in the parent. **No sibling expected and the fields are a deliberate subset against constants** → keep as per-field, document the subset intent (not every subset becomes a whole-object comparison). See `recursive-comparison.md` for decision guide. |
| A54 | Test helper duplicates production method | For each private/package method in the test class, check if a production class used in the test has a method with identical logic (same stream/filter/find pattern, same computation). Compare the test helper's body against methods on the objects it operates on — including private methods that could be made public. | Any match → make the production method accessible (public or package-private), delete the test helper, call the production method instead |
| A23 | Cross-Statements assertion duplication | For each `assert*` method in the target Statements class, grep all other `*Statements.java` for methods asserting the same domain concept (same response fields, same status checks). Example: asserting `in_progress` status + `assignee` + `priority` when `GetTaskStatusStatements.assertInProgressTask()` already exists. | Same domain assertion logic in 2+ Statements → delegate to existing Statements |
| A24 | Assertions in test class | Grep `assertThat\|assertThatThrownBy` in test class (not Statements). Example: `assertThatThrownBy(...)` or `assertThat(response.field())` directly in a test method instead of `statements.assertX(response)`. | Any assertion in test class → move to Statements method |
| A37 | Control flow in test class | Grep `for \|for(\|while \|while(\|if \|if(` in test methods (not Statements, not base class helpers). Example: `for (int i = 0; i < 10; i++) { statements.assertField(i); }` directly in a test method. | Any loop or conditional in test class → extract to Statements method |
| A41 | Loops/conditionals computing expected values in tests | Grep `for \|for(\|if \|if(` combined with assertion or expected-value derivation in Statements. Loops for bulk data generation or collection assertions are fine. Example violation: `if (total > pageSize) { expected = total % pageSize; }` | Loops/conditionals that compute expected values or make branching assertions are production logic leaking into tests → replace with literal constants |
| A31 | Statements dependency count | Count `private final` fields in a Statements class — each is an injected dependency (usecases, other Statements, Fakes, Clock) | >8 dependencies → split Statements by concern |
| A38 | Middleman delegators between Statements | Methods in a Statements class whose entire body delegates to an injected Statements dependency (e.g., `void assertX() { otherStatements.assertX(); }`). List each wrapper → target Statements + method. | Any pass-through → remove method, have tests inject the target Statements directly |
| A39 | Implementation constants in test class | Grep for numeric literals (`\d+L`), `BigDecimal.valueOf`, `new .*Request`, technical constants (task IDs, column IDs, positions, offsets) passed as arguments to ANY Statements call (setup, action, or assertion) in test methods. Compare with the `@Description` — test code should match its Gherkin abstraction level. | Any implementation constants in test class → encapsulate inside the Statements method, return a record with values needed by subsequent calls. |
| A40 | Calculated expected values in tests | Grep `Math\.\|ceil\|floor` and arithmetic (`+`, `-`, `*`, `/`) used to compute expected assertion values from runtime data in Statements or test classes. Example: `int expectedSize = (int) (totalElements - (lastPageNum - 1) * pageSize)`. | Any formula computing an expected value → tests must be dumb. Fix setup to produce deterministic data, then assert with literal constants. |
| A53 | Null assertion on domain VO field | Grep `isNull()` in Statements/test. For each match, check if the asserted expression traverses a domain entity or value object (e.g., `task.getDescription().getValue()`). | Any `isNull()` on a domain VO field → domain is null-free; fix the VO to reject null (empty string / Optional / Null Object), update assertion to match |

**Frontend-specific** (skip if not `.tsx`):

| # | Check | Enumerate | Violation |
|---|-------|-----------|-----------|
| A15 | Component size | JSX return block line count | > 100 lines |
| A15b | Distinct visual blocks | Count top-level sibling JSX sections in return (e.g., header div, warning banner, stats grid, content card). Each block has its own data/props with no cross-block shared state. | 3+ separable blocks → extract each into its own component file, even if total lines < 100 |
| A16 | Return branches | `return` statements with JSX in component function | 2+ return blocks with JSX |
| A17 | Logic in component | Validation, computation, `fetch` calls inside `.tsx` | Any business logic or fetch |
| A18 | Render body locals | Computed local variables declared inside component before return | Any computed local |
| A19 | Repeated class strings | `className` values appearing 2+ times across JSX | Any repeated className string |
| A46 | Raw value not a theme token | **MUST grep first:** run `Grep pattern="\[#[0-9a-fA-F]\|\[['\"]" path="<target-file>" output_mode="content"` and paste ALL matching lines with line numbers. Then read the theme stylesheet `@theme` block to list existing tokens. | Any arbitrary color or font in a `className` (`bg-[#f1f3f5]`, `font-['Manrope']`) → add a token to `@theme` and use the named utility. Arbitrary geometry (`top-[-7.5rem]`, `rotate-[3deg]`) stays. List each: line number, value, proposed token name. |
| A60 | `px` lengths in CSS | **MUST grep first:** run `Grep pattern="[0-9]px" path="<target-file>" output_mode="content"` over `.tsx`, `.css` and inline `style={{}}` and paste ALL matching lines with line numbers. | Any length in `px` other than a `1px`/`2px` border/outline hairline or a media-query breakpoint → rewrite in `rem` at `1rem = 16px` (`15px` → `0.9375rem`). List each: line number, current value, converted value. |
| A47 | Repeated conditional className | Same conditional className expression (ternary, logical AND, template literal with conditions) appearing in 2+ JSX elements, branching on the same variable to select classes. Example: `isActive ? 'bg-blue-500 text-white' : 'bg-gray-200'` repeated across elements. | 2+ occurrences → extract into a helper function (e.g., `getStatusClassName(status)`) above the component |
| A57 | Component styles in the theme stylesheet | Read the theme stylesheet. List every selector outside `@theme`, `:root`, `@layer base`, `@keyframes`, `@font-face`, and every `@apply` outside `@layer base`. | Any such selector → move its declarations into the component that uses the class as Tailwind utilities on the markup, then delete the selector. A `@layer components` block existing at all is a violation. List each: selector, consuming component file. Chain length in a `className` is never a smell. |

## Section B — Read-and-judge (cite evidence)

**Test-specific** (skip if not a test file):

| # | Question | Evidence required |
|---|----------|------------------|
| B10 | Do test helper methods use hardcoded values that should vary per test? | Quote the hardcoded value |
| B11 | Does the test create an object only to pass it to a single Statements method for assertion? | Quote the create + pass |

**Frontend-specific** (skip if not `.tsx`):

| # | Question | Evidence required |
|---|----------|------------------|
| B12 | Is this component generic enough to be reused across features? Should it live in `shared/ui/`? | Quote the component's props and usage |
