# React/TypeScript Infrastructure Idioms

Tech binding for `infrastructure.md`. Load alongside the universal rules.

## Commands

- Execute commands with `frontend` as the working directory.
- Dev server: `npm run dev`.
- Run tests: `npx vitest run`.

## Environment Variables

- `VITE_API_URL` is a required, explicit API base URL in the frontend's own local
  environment (`frontend/.env.local`) or deployment environment.
- Frontend configuration never reads `BACKEND_PORT` or the API application's `.env`.
- Deployment infrastructure injects `VITE_API_URL` at build/runtime according to the
  frontend hosting model.
- Vite client configuration uses `import.meta.env.VITE_*`. Required external URLs have
  no fallback; optional values may use `import.meta.env.VITE_VAR ?? 'fallback'`.

## Process Safety

- Dangerous commands for Node: `taskkill //IM node.exe`, `pkill node` -- these kill ALL instances system-wide.
