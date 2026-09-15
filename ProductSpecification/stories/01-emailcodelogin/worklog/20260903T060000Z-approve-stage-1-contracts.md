# 4.1 Существующий пользователь получает сессию по верному коду — approve stage-1 contracts

Started: 2026-09-03T06:00:00Z

Outcome: APPROVED — «годится, замораживай весь шов»

## Что одобрено

Весь шов `verify` замораживается целиком, включая две вещи, которые сценарию 4.1 не нужны и
оправданы только Tier 2: `find_challenge` (проверка формы кода до траты попытки — сценарий 3.1)
и `remember_verification`/`find_verification` (окно повтора — сценарий 6.1). Размен назван явно
перед решением: одна заморозка сейчас вместо трёх разморозок порта на 4.2, 5.1 и 6.1.

Одобренный контракт и его обоснование — `decisions/challenge-verify-contracts-decision.md`.
План Stage 2 — блок `<!-- stage-2-plan: ... -->` в
`worklog/20260903T050000Z-stage-1-acceptance-red-contract-design.md`, пять полос:
usecase, adapter-cache, adapter-storage, adapter-rest, application.

## Предпосылка Stage 2, применённая координатором при одобрении

Не принадлежит ни одной полосе — иначе полосы стали бы зависимыми.

- `infrastructure/.env` (генерируемый, вне git) дописан четырьмя переменными:
  `AUTH_CHALLENGE_REPLAY_WINDOW_SECONDS=60`, `ACCESS_TOKEN_TTL_SECONDS=1800`,
  `REFRESH_TOKEN_TTL_SECONDS=31536000`, `JWT_SECRET`. В `.env.example` и `setup-ports.sh`
  они уже приехали коммитом проектной полосы 8c5ac53, поэтому новый репозиторий получит их сам.
- `PyJWT` в `requirements.txt` **не нужен**: сторонние зависимости живут в pyproject модулей, а
  `pyjwt>=2.9` уже объявлен в `backend/application/pyproject.toml` тем же коммитом. В окружении
  установлен (2.13.0). Пункт предпосылки из отчёта проектной полосы закрыт как неверно
  адресованный, а не как невыполненный.

## Расхождение, принятое вместе с дизайном

Отгруженный обработчик `UnauthorizedException` отдаёт `payload: null` и единое сообщение, что
спорит с `endpoints.md` и `auth_challenge_verify.yaml`. На 4.1 не наблюдаемо; чинится на 5.1/5.4,
которые эти ответы и утверждают.

## Проверки

Ничего не исполнялось: это шаг решения. Состояние на входе не менялось —
backend 36 passed, acceptance 5 collected (тест 4.1 skip-marked).
