# Frontend Rules

## Humble Object Pattern

- Pure logic in logic files: validation, state computation, request building, data mapping. No side effects.
- HTTP client in API client files: fetch calls, response mapping, error handling.
- Component files are thin wrappers: call logic + API, translate UI state from logic files, render markup.
- FORBIDDEN in component files: business logic, validation regex, direct fetch calls, request building.

## Mockup Placeholder Data

Mockups contain placeholder values (`user@example.com`, fake dates, sample prices). NEVER copy these into components as hardcoded strings. User-specific data (email, name, company) must come from auth context or API responses. If a value is different per user or per session, it must be dynamic.

## Component Size

- When a component file exceeds ~70-100 lines, extract sub-components (views, sections, cards) into their own files in the same `components/` directory.
- Page components should be thin routers/orchestrators -- fetch data, route between views, render child components.
- Helper components used by only one view live in that view's file. When a helper is shared across views, give it its own file.

## Feature Structure

- Features are organized in self-contained directories with subdirectories for components, logic, API clients, and tests.
- Feature-specific components stay in the feature's components directory.
- Reusable components shared across features live in a dedicated shared UI directory.

## Naming

- Logic functions: verb+noun (`validateEmail`, `buildRegistrationRequest`, `isFormValid`).
- API functions: verb+noun matching endpoint (`registerUser`, `verifyEmail`).
- Types: `{Feature}Request`, `{Feature}Response`, `{Feature}FormState`.
- Test blocks: use the test runner's block and case syntax (see tech binding for specific conventions).

## Testing

- Logic tests: pure functions, no DOM, no framework rendering. Use the frontend test runner (see technology.md Conventions).
- API client tests: frontend test runner + HTTP mock library.
- The test skip marker (see technology.md Conventions) is the frontend equivalent of the backend test disable marker. Comment above the skip documents failure reason.
- Use the native `fetch` API (not axios). Base URL from the backend URL environment variable.
- **NEVER hardcode `http://localhost:8080`** in HTTP mock handlers or production code. Use the backend URL environment variable -- the test runner sets it dynamically from the backend port. Production API clients read the variable with a fallback to empty string. HTTP mock tests read the variable for handler URLs.

## Parallel Frontend Lane Ownership

In staged frontend work, a worker may edit only the explicit file manifest assigned
by the coordinator. Stage 1 interface-only files are read-only during Stage 2.
Reject a design that co-locates a frozen contract with behavior a Stage 2 lane must
implement; separate the interface before dispatch. Never stage, commit, or edit
`progress.md` from a lane.

Before editing, compare the needed path with every lane manifest. If it is owned by
another lane, is a frozen interface, was dirty at dispatch, or was not declared,
stop and return the path plus the required change to the coordinator. Do not widen
ownership, copy the behavior elsewhere, or make a compatible-looking interface
change locally. A lane computes changes only inside its manifest relative to the
recorded baseline; concurrent peer changes do not belong to its diff. A lane
succeeds only when those paths and its complete lane checks pass.

## Selenium Tests

- 2-tier DSL: Test Class (thin, reads like English) + Statements Class (locators, actions, assertions).
- Use `data-testid` attributes for locators. Components MUST include them.
- FORBIDDEN locator strategies: class-based selectors, tag-based selectors, raw CSS class selectors. These break when styling changes. Always use `data-testid`.
- FORBIDDEN in-app navigation via URL: never use direct URL navigation to move between pages. Tests must navigate through UI interactions (clicking buttons, links, menu items). Allowed direct URL uses: (1) app root as test entry point, (2) external entry points where users genuinely arrive via URL -- deep links, shared links.
- Page Statements own browser interactions only (`navigate*`, `enter*`, `click*`, `assert*`). All infrastructure and backend setup (mock stubs, API calls, mock configuration) goes through backend Statements that the test injects directly -- never delegated through page Statements.
- Full conventions in red-selenium and green-selenium skill templates.
- **Known driver/env traps:** `infrastructure/notes/acceptance-test-gotchas.md` records the Playwright driver-singleton poisoning failure (and its `discardBrowser()`/`ensureBrowser()` fix) — read it if browser sessions behave inconsistently across tests.
- **Mass failure diagnosis:** When all E2E browser tests fail uniformly (connection errors, timeouts), the cause is infrastructure -- not browser/driver versions. Re-verify backend is alive (health endpoint) before investigating individual tests. A dead backend causes frontend pages to error out, the browser driver to time out, and connections to reset -- which looks like a browser compatibility issue but isn't.
- **Assertion detail level:** Assertions must match spec detail level -- when the spec says "cards with title, status, assignee, and priority", verify each sub-element within each card and assert visible + non-empty. A count-only check loses the spec's intent. Read the DSL Technical Reference table in the test spec.

## Conditional Class Logic

- When the same conditional class expression (ternary, logical AND, or template literal with conditions) appears in 2+ elements, extract it into a helper function (e.g., `getStatusClassName(status)`) above the component. The helper takes the condition value and returns the class string.
- This applies to any repeated branching over the same variable to produce class strings.
- Single-use conditional classes are fine inline. The trigger is repetition.

## Styling Placement

- **The theme stylesheet holds only what is global.** Design tokens (colors, fonts, radii, shadows), CSS variables, the base layer (body, resets, default typography), font imports, and keyframes. Nothing in it names a component: no `.auth-card`, no `.btn-primary`, no component layer at all. If a selector would only ever match one component's markup, it is not global.
- **A component's styles live in the component, as utility classes on its markup.** The reader of a component sees its whole appearance in the file they already have open; a class name that points into a stylesheet is one indirection the reader must chase and one file that silently drifts when the markup changes.
- **A color, font, or measure that is not a token is a leak.** A raw hex color or font name in a component means the design has a value the theme does not know. Add the token to the theme and reference it by name; never inline a raw value and never hide it in a stylesheet class. The utility syntax is in the CSS tech binding.
- **Repetition is solved with components, not classes.** The same utility set in 2+ components is a shared component in the shared UI folder (see the "Shared UI" rules), not a CSS class. The same set repeated within one component is a `const` above the component. Conditional class selection follows "Conditional Class Logic" above.
- **Long utility chains are fine.** Length is not a smell; a chain is the component's stylesheet, and the file-size limit is the only bound. Break a long `className` across lines with a template literal or a constant when it hurts reading -- never by moving it out of the component.

## CSS Units

- **Lengths are `rem`, never `px`.** Font sizes, spacing, sizing, radii, shadows, offsets -- every length in the theme stylesheet, in arbitrary-value utilities, and in inline styles is written in `rem`. A `px` value ignores the user's root font-size preference and breaks proportional scaling of the whole layout; `rem` keeps every measure relative to one root.
- Convert from the mockup at the root ratio (`1rem = 16px`): `12px` -> `0.75rem`, `15px` -> `0.9375rem`, `24px` -> `1.5rem`. Never round to a "nicer" value -- the mockup is the source of truth, the unit is the only thing that changes.
- **Exactly three `px` exemptions**, each because the value is physically not a length the user scales: hairline borders and outlines (`1px`, `2px`), media-query breakpoints (a viewport width is a device fact, not a typographic one), and `0` (unitless).
- Utility-framework scale tokens already resolve to `rem` and are not affected; the rule bites on arbitrary values, theme-stylesheet rules, and inline styles. Framework-specific syntax is in the CSS tech binding.

## Icons

- ALWAYS use the icon library (see tech binding) -- never write inline SVG paths or elements. Claude generates broken/unrecognizable SVG paths.
- Use the icon library's components which render correct, tested SVGs.
- Standard sizes: small for inline text, medium for nav items, large for prominent display.
