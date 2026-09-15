# Local Dev Gotchas

## REPO_INDEX collisions

`setup-ports.sh` derives `REPO_INDEX` from the **trailing digits of the repository
directory name** (`uwords-api` → `0`, `uwords-api2` → `2`). Two clones whose directory
names end in the same digits get the same ports and will fight over them. Fix it by
regenerating with an explicit index:

```bash
REPO_INDEX=3 FORCE=1 infrastructure/scripts/setup-ports.sh
```

## `.env` is generated, never committed

`infrastructure/.env` is gitignored. `infrastructure/.env.example` documents the shape.
Every script sources `.env` through `scripts/_env.sh` and regenerates it if missing —
so no script ever hardcodes a port.

## Startup order matters

`run-infra.sh` → `migrate.sh` → `run-backend.sh`. The application does not migrate on
boot; a backend started against an unmigrated database will fail on the first query, not
at startup.

## Stopping things

- Backend: `stop-backend.sh` kills only the PID listening on this instance's `BACKEND_PORT`.
- Containers: `stop-infra.sh` touches only the `uwords-$REPO_INDEX` compose project.
  Containers with another suffix belong to another session — leave them alone.
