# React/TypeScript TDD Conventions

## Testing Framework

- Logic tests: Vitest, pure functions, no DOM, no React.
- API client tests: Vitest + MSW (Mock Service Worker).

## Test Skip Marker

- `.skip` is the test skip marker. Comment above `.skip` documents failure reason.

## Base URL Configuration

- Base URL resolved via `import.meta.env.VITE_API_URL`.
- Vitest receives an explicit `VITE_API_URL` from the frontend test environment; it
  never derives one from `BACKEND_PORT`.
- Only the shared client (`src/shared/api/main/api-client.ts`) reads `VITE_API_URL` and it fails
  fast when the variable is missing; an empty-string fallback is forbidden because it
  silently changes an external API call into a same-origin request. Feature `.api.ts`
  files receive an `ApiClient` and never read the variable themselves.
- MSW tests: `const BASE = import.meta.env.VITE_API_URL`.
