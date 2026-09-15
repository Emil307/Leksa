# Frontend infrastructure

Local scripts, executed from `frontend/`:

| Script | Purpose |
|---|---|
| `infrastructure/scripts/setup-ports.sh` | Generates `infrastructure/.env` (`FRONTEND_PORT` = 5173 + repo index) |
| `infrastructure/scripts/run-frontend.sh` | Starts the Vite dev server on `FRONTEND_PORT`; PID in `infrastructure/run/`, log in `infrastructure/logs/` |
| `infrastructure/scripts/stop-frontend.sh` | Stops the dev server started by `run-frontend.sh` |
| `infrastructure/scripts/test-e2e.sh [filter]` | Runs the Selenium suite in `e2e/` against the running dev server; the dev server must have been started as `E2E_STUB=1 run-frontend.sh` so `VITE_API_URL` points at the in-process API stub on `E2E_API_STUB_PORT` |

`VITE_API_URL` is read only from `frontend/.env.local` (copy `.env.example`) or the deployment
environment; it is never derived from the API's `infrastructure/.env`.
