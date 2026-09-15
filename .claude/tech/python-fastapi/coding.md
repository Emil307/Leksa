# Python/FastAPI Coding Idioms

Tech binding for `coding-rules.md`. Shared section structure: `.claude/templates/coding/coding-sections.md`.

Stack: FastAPI + SQLAlchemy 2.0 (async) + Alembic + pydantic-settings.
Modules follow the universal layout — `backend/{domain,usecase,adapters/*,application}`, each an
installable Python package with its code under `src/` (e.g. `backend/adapters/storage/src/`).

## Deployment

- In-memory state to avoid: module-level `dict`/`set`, mutable default arguments, singleton caches in closures, class-level mutable attributes. Shared state → the database (or a cache service reachable from every instance). Factory functions that cache a *stateless* service/repository instance are wiring, not state — allowed.

## Clean Architecture

- `domain`: Pydantic `BaseModel` entities via a `DomainEntity` base — no SQLAlchemy, no FastAPI imports. Entities + `XCreate`/`XUpdate` input models + enums + exceptions only.
- `usecase`: application services + ports declared as `Protocol` classes. Imports domain only. No FastAPI, no SQLAlchemy session/query code.
- `adapters`: `rest` (FastAPI routers, request/response schemas), `storage` (SQLAlchemy repositories, `XModel` ORM models, mappers, `UnitOfWork`), `email`, `scheduling`, `security`, external API clients. Framework code lives ONLY here.
- `application`: the FastAPI app factory, `lifespan`, and manual wiring of adapters into services.

## Domain-Driven Design

- Validation: raise a `BaseDomainException` subclass with an `ErrorCode` (e.g. `ValidationException`), never a bare `ValueError`.
- Enum: `enum.Enum` / `StrEnum`; string codes as `class ErrorCode(str, Enum)`. `.value` for the wire form.
- Optional: `Optional[T]` / `T | None`. Collections: `list` for mutable, `tuple`/`frozenset` for immutable.
- Forbidden dispatch: `isinstance` / `type()` branching in domain and usecase. Dispatch on an enum field or via a mapper in the adapter.
- Typed list: `list[User]`, never `list[BaseModel]` + `isinstance`.
- Parameter object: a dedicated Pydantic `BaseModel` (`XCreate`, `XUpdate`) or `@dataclass`.
- Entity mutation: Pydantic `model_copy(update=...)` (see `DomainEntity.update`) — do not mutate in place across layers.

## Code Generation

- DTOs/VOs: Pydantic `BaseModel` (domain) or `@dataclass(frozen=True)` (pure value objects with no serialization need).
- DI: manual `__init__` wiring; module-level factory functions (`get_x_service()`, `get_x_repository()`) return cached singletons. Builders: `@classmethod` (`create`, `of`, `from_`).

## Naming

- ORM model: `{Name}Model` in `backend/adapters/storage/src/models/`. Domain entity: `{Name}`.
- Mappers: `{Name}Mapper` in `backend/adapters/storage/src/mappers/` with `to_domain()` / `build_create_dict()` / `build_update_dict()`.
- Repository: `{Name}Repository(SQLAlchemyRepository)` with `model = {Name}Model`.
- Service: `{Name}Service` in `backend/usecase/src/services/`. Modules: `snake_case`.

## Immutability

- Value objects with no I/O: `@dataclass(frozen=True)`. Domain entities: Pydantic models mutated via `model_copy`.

## Accessor Chains

- `a.b.c` deep access → add a convenience `@property` on the entity (e.g. `User.display_name`).

## Optional/Nullable Handling

- `x or default` for defaults; ternary / `match` for mapping. Never `if x is not None: return x.value` chains.
- Repository reads return `Optional[Entity]`; callers handle `None` explicitly.

## Null Boundary

- Routers: validate/`or None` before building DTOs. Request models: `Optional[T] = None` fields.

## Request DTO Conversions

- Convert at the REST boundary: `str`→`datetime`, `str`→enum via `parse()`. Method names like `to_usecase_request()`.

## Branching

- `match`/`case` over long `if/elif/return` chains (Python 3.10+).

## Local Variables

- Type inference (no annotation) is idiomatic in Python — not forbidden. Annotate public signatures and non-obvious locals.

## Controllers (FastAPI routers)

- Return Pydantic response models or `JSONResponse(content, status_code=...)`. Errors bubble to the centralized `@app.exception_handler` registered by the app factory — do not try/except-and-swallow in the router.
- A router must not call another router; it delegates to exactly one service.

## Storage Adapters

- ORM `XModel` ≠ domain entity. Convert via the mapper (`to_domain()` / `build_create_dict()`), never return `XModel` outside the repository.
- Build queries with SQLAlchemy `select(...).where(...)`; no manual row-dict grouping, no `itertools.groupby`/`defaultdict` assembly.
- Transactions via the `UnitOfWork` async context manager; never open raw sessions in services.

## Refactor Agent — Python Terms

| Generic term (in agent) | Python equivalent |
|--------------------------|-------------------|
| Qualified enum references in logic | `from module import EnumValue` instead of `Module.EnumValue` |
| Type-checking/type dispatch in domain or usecase | `isinstance`, `type()` checks |
| Base-type list re-partitioned with type checks | `list[BaseModel]` + `isinstance` |
| Immutable data class | `@dataclass(frozen=True)` / Pydantic with frozen config |
| Collection pipeline terminal operation | `list()` / comprehension terminal |
| Manual per-field assertion for immutable data types | frozen dataclasses and Pydantic value objects |

## Scan Checklist — Storage Grep Patterns

| # | Grep pattern / indicator |
|---|--------------------------|
| A33 | `itertools.groupby`, `defaultdict(list)`, manual row-dict assembly |
| A34 | Count `Repository()` / model references injected per service |
| A42 | Static methods returning SQLAlchemy `select`/`where` clauses from a filter object |
| A43 | `.mappings()`-less raw `Row` tuple indexing (`row[0]`) |
| A44 | Inline `select().where().join()...` chains >5 lines in a repository method |

## HTTP Clients

- Production async: `httpx.AsyncClient`. Tests: `unittest.mock` / `respx` at the adapter boundary.

## Error Handling

- Base: `BaseDomainException(Exception)` with `ErrorCode`, `payload`, `expose_to_user`. Centralized handler: FastAPI `@app.exception_handler` registered in the app factory.
