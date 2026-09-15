# Coding Rules

Always-on architectural core. The DDD smell catalogue, code-style catalogue, and
per-layer rules (usecases, controllers, storage adapters, error handling) live in
`.claude/guidelines/coding-detail.md` — read it before writing or refactoring code
in any backend layer.

## Deployment

- The backend runs as multiple instances. Never store application state in-memory (hash maps, static/global fields, local caches). Use the database for any state that must be consistent across instances.

## Clean Architecture

- `domain`: NO dependencies (only code generation library). No framework annotations.
- `usecase`: depends only on domain. No framework code except dependency injection and transaction management.
- `adapters`: implement interfaces defined in usecase. Framework-specific code lives here (HTTP controllers, message listeners/publishers, database repositories, external API clients).
- `application`: wires everything together.
- `acceptance`: top-level API black-box module. Tests use HTTP only and have no dependency on backend internals.
- Independently deployed client applications keep their production code, tests, and E2E harnesses inside their own application roots and communicate with the backend only through its external API.
- Dependency flow is strictly inward. FORBIDDEN: importing adapters from usecase/domain, importing usecase from domain, importing framework code from domain/usecase, **injecting or calling one usecase from another usecase**.
- Adapter interaction rules: first-layer adapters (controllers, listeners) must not call other first-layer adapters — they delegate to usecases. Third-layer adapters (repositories, clients) must not call other third-layer adapters or usecases — they are called by usecases only.
- Usecase interaction rule: usecases must not call other usecases. Each usecase is a top-level entry point that orchestrates one user-visible operation; usecases do not compose. If two usecases share logic, extract it into the domain layer (a domain method, value-object behavior, or a stateless domain service) or into a shared helper that is itself not a usecase. Chaining usecases hides the call graph from the controller layer, leaks transactional/authorization boundaries across operations, and entangles top-level scenarios that should evolve independently.

## File Size

- **Hard limit: 200 lines per file.** After any creation or refactoring, verify with `wc -l`. If a file exceeds 200 lines, split it further. This applies to **every source file regardless of type** — production code, test classes, Statements classes, API clients, stylesheets, and config files. The limit is not class-specific: a file with no classes (a stylesheet, a config file) is still capped at 200 lines. Third-party generated files (shadcn/ui) are exempt.

## No Comments

- **Source files carry no comments and no docstrings.** Not module docstrings, not class or method docstrings, not inline `#`/`//` comments, not section labels, not rationale notes. This applies to production code, tests, Statements, fakes, clients, and DTOs alike. Names, types, and tests carry the meaning; anything they cannot carry belongs in documentation, not in the source.
- **Do not write one and delete it later.** The rule governs authoring, not cleanup. A comment that explains a non-obvious choice is a signal the code needs a better name, a smaller method, or an extracted type — make that change instead of annotating the confusing shape.
- **Durable rationale has a home outside the code**: the story's `decisions/*-decision.md` for an architectural choice, `endpoints.md` for a wire contract, `interview.md` for a captured constraint, `ProductSpecification/` for a reference. Relocate it there and leave the source silent.
- **Exactly two exemptions**, both because a reader or a tool consumes them as data rather than as prose:
  - The **Gherkin scenario on an acceptance test class** — the scenario description mandated by `.claude/rules/workflow.md` ("Where the Current State Lives") and the tech binding's acceptance test-class template. It is the current-state documentation of the product; nothing else records it.
  - **Migration comments**, per the `CLAUDE.md` project convention.
- Configuration files (`pyproject.toml`, `.importlinter`, compose files) are outside this rule: a comment there is a tooling directive addressed to whoever edits the config.

## Domain Package Layout

- **A flat `domain/{subsystem}/` folder is a dump waiting to happen.** Group by the concept that owns the type, never by "everything auth". Under `domain/auth/` the kernel is split into `challenge/` (the method-agnostic challenge lifecycle), `session/` (tokens and their policies), and `user/` (who the person is — the email, the profile, the account).
- **Every authentication method gets its own package**: `domain/auth/email_code/`, and — when they land — `domain/auth/telegram/`, `domain/auth/oauth/`. Everything a method does not share with the others (its strategy, its message template, its method-specific value objects) lives there and nowhere else. A method's type must never be added to the shared kernel "for now": the kernel is what all methods have in common, and one method's type in it makes the next method carry weight it does not use.
- **Dependency direction inside `domain/auth/`**: a method package imports the kernel; the kernel never imports a method package. A shared type that only one method can satisfy is a design defect — record it in the story's `decisions/*-decision.md` and untangle it before the next method arrives, rather than hiding it by moving files.
- The same shape applies to any subsystem with pluggable variants — payment providers, notification channels, import formats: a shared kernel plus one package per variant.
