# React/TypeScript Coding Conventions

Tech binding for `frontend-rules.md`. Shared section structure: `.claude/templates/coding/coding-sections.md`.

## Formatting

- Every statement ends with a semicolon. Formatting is owned by Prettier (`frontend/.prettierrc.json`:
  `semi: true`, single quotes, `printWidth: 120`, `trailingComma: es5`); run `npm run format`
  after writing or editing any `.ts`/`.tsx`/`.css` file and `npm run format:check` before a commit.
- Prettier may push a file over the 200-line limit by wrapping long lines; the fix is a smaller
  fixture, an extracted helper, or a split file — never a formatter exception.

## File Extensions (Humble Object)

- Logic files: `.logic.ts`
- API client files: `.api.ts`
- Component files: `.tsx`

## Feature Structure

- Features live in `frontend/src/features/{feature}/` with subdirectories:
  - `components/` -- React components: `{Feature}Page.tsx` and extracted sub-components.
  - `logic/main/` -- pure logic `{feature}.logic.ts`; `logic/test/` -- its Vitest tests
    `{feature}.logic.test.ts`.
  - `api/main/` -- `{feature}.api.ts` (the client class), `endpoints/*.endpoint.ts`,
    `dto/*.dto.ts` (see below); `api/test/` -- its Vitest tests `{feature}.api.test.ts`.
  - `types/` -- frozen interface files.
- **Tests sit beside the code they test, split `main/` / `test/` like the backend's
  `src/main/java` / `src/test/java`.** Every folder that holds testable code (`logic/`, `api/`,
  `shared/api/`, `shared/utils/`) has exactly two children: `main/` with production files and
  `test/` with their tests. There is no feature-wide or module-wide `__tests__/` folder. A test
  imports its subject as `../main/{file}`; a folder with a public `index.ts` keeps it at the
  folder root re-exporting from `./main/...`, so `@/shared/api` and `@/shared/utils` stay stable.

## Shared UI Components

- Reusable components live in `frontend/src/shared/ui/` — never under `src/app/`, which holds only the composition root (`App.tsx`, `theme.css`).
- Examples: `field-error.tsx`, `loading-spinner.tsx`, `password-toggle.tsx`, `input-styles.ts`.

## Shared API Client

- One HTTP client for the whole app lives in `frontend/src/shared/api/main/`: `api-client.ts`
  (`class ApiClient` built from `{ baseUrl, timeoutMs }`, the default `apiClient` bound to
  `VITE_API_URL`), `api-error-mapper.ts` (`class ApiErrorMapper`), `api-error.types.ts` (the one
  frontend error union), `unexpected-response.ts` (`reportUnexpectedResponse`), and their types.
- The shared client owns transport **and** the whole error protocol: `fetch`, JSON encoding,
  timeout via `AbortController`, body parsing, and — through `ApiErrorMapper` — the mapping of
  every backend status / `ErrorCode` to the frontend `ApiError` union, once, for every endpoint:
  400 `VALIDATION_FAILED` → `validation-failed`, 401 `UNAUTHORIZED` → `unauthorized`, 403 →
  `forbidden`, 404 → `not-found`, 409 `CONFLICT` → `conflict` carrying `payload.retryAfterSeconds`
  (or `null`), 503 and timeout → `unavailable`; an unknown status, an envelope whose code
  disagrees with the status, or a 200 body the endpoint cannot parse → reported once and returned
  as `{ kind: 'unexpected', status }`. The envelope `message` never reaches feature code.
- Status **behaviour** lives in the mapper as well — the retry hint on 409 today, token refresh
  on 401 when it lands. Feature code never branches on HTTP statuses, envelope codes, or invents
  its own error kinds (`invalid-email`, `cooldown`, `rejected` are screen states derived in
  `logic/` from `ApiError`, never returned by an endpoint).
- A feature's `api/` mirrors the backend REST adapter (controller / DTO) and never calls
  `fetch`, reads `VITE_API_URL`, or looks at error responses:
  - `{feature}.api.ts` — one class per feature (`AuthChallengeApi implements ChallengeApiClient`),
    constructed with an `ApiClient`; each method is a single `this.api.call(endpoint, request)`,
    like a controller method that only delegates. The module exports the class and one default
    instance (`authChallengeApi = new AuthChallengeApi(apiClient)`); it never exports loose
    method functions — importers call `authChallengeApi.startChallenge(...)` themselves.
  - `endpoints/{operation}.endpoint.ts` — one `ApiEndpoint<Success>` per operation: `path` and
    `parse(body)` (the success DTO, or `null`). Nothing else.
  - `dto/{name}.dto.ts` — one class per success wire shape with `static parse(body): Dto | null`
    (the validating reader of the JSON) and a `toXxx()` converter to the feature type, the
    frontend twin of the backend `XxxDto.from(...)` / `toUsecaseRequest()` records.
- Outcome unions are `ApiOutcome<XxxSuccess>` = `XxxSuccess | ApiError`. Tests build the class
  from `new ApiClient({ baseUrl: BASE, timeoutMs })` against MSW.

## Shared Utilities

- Generic helpers with no feature or transport knowledge live in `frontend/src/shared/utils/`,
  grouped by concern in kebab-case files under `main/` and re-exported from `index.ts`: `guards.ts` (type
  guards such as `isString`, `isPositiveNumber`, `isJsonObject`), `text.ts` (`countUtf8Octets`).
- Never define a private `isString`/`isNumber`/`clamp`-style helper inside a feature or inside
  `shared/api`; add it to the matching `shared/utils` file (or a new one) with a unit test in
  `shared/utils/test/`, and import it from `@/shared/utils`.
- A helper that names a domain concept (`joinCode`, `validateEmail`) is feature logic, not a
  utility — it stays in the feature's `logic/`.

## Icon Library

- React icon library: `lucide-react`.
- Import: `import { Plus, X } from 'lucide-react'`.
- Usage in JSX: `<Plus className="w-4 h-4" />`.
- Standard sizes: `w-4 h-4` (small), `w-5 h-5` (medium), `w-6 h-6` (large).

## Conditional className Syntax

- Ternary: `isActive ? 'bg-blue-500' : 'bg-gray-200'`.
- Logical AND chains and switch-based class selection in JSX.
