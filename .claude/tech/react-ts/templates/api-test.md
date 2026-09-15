# Frontend API Client Test Template

## Backend Endpoint Pre-Check

See `.claude/templates/workflow/api-test-pre-check.md` for the full pre-check procedure.

## Test File

Location: `frontend/src/features/{feature}/api/test/{feature}.api.test.ts`

```typescript
import { describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from '@/test/msw-server'
import { ApiClient } from '@/shared/api'
import { RegistrationApi } from '../main/registration.api'
import type { RegistrationRequest } from '../../types'

const BASE = import.meta.env.VITE_API_URL

if (!BASE) throw new Error('VITE_API_URL is required for frontend API tests')

const PATH = '/api/v1/auth/register'
const REQUEST: RegistrationRequest = { email: 'user@example.com', password: 'SecurePass123' }
const client = new RegistrationApi(new ApiClient({ baseUrl: BASE, timeoutMs: 10000 }))

describe('Registration API client', () => {
  it('should post the request and return the registered outcome', async () => {
    let receivedBody: unknown = null
    server.use(
      http.post(`${BASE}${PATH}`, async ({ request }) => {
        receivedBody = await request.json()
        return HttpResponse.json({ userId: 'user-1' }, { status: 200 })
      })
    )

    const outcome = await client.registerUser(REQUEST)

    expect(receivedBody).toStrictEqual(REQUEST)
    expect(outcome).toStrictEqual({ kind: 'registered', user: { userId: 'user-1' } })
  })

  it('should map 409 CONFLICT to the shared conflict kind', async () => {
    server.use(
      http.post(`${BASE}${PATH}`, () =>
        HttpResponse.json({ code: 'CONFLICT', message: 'secret', payload: {} }, { status: 409 })
      )
    )

    expect(await client.registerUser(REQUEST)).toStrictEqual({ kind: 'conflict', retryAfterSeconds: null })
  })
})
```

## Stub

Create the minimal class in `api/main/{feature}.api.ts`; the shared client in `@/shared/api`
already owns `fetch` and `VITE_API_URL`, so the stub imports nothing but types:

```typescript
import type { ApiClient } from '@/shared/api'
import type { RegistrationApiClient, RegistrationOutcome, RegistrationRequest } from '../types'

export class RegistrationApi implements RegistrationApiClient {
  constructor(private readonly api: ApiClient) {}

  registerUser = async (request: RegistrationRequest): Promise<RegistrationOutcome> => {
    throw new Error('Not implemented')
  }
}
```

Tests build the class from the shared client against MSW:
`new RegistrationApi(new ApiClient({ baseUrl: BASE, timeoutMs: 10000 }))`. Assert the shared
error kinds (`validation-failed`, `conflict`, `unauthorized`, `unavailable`, `unexpected`), never
feature-invented ones.

## MSW Setup

MSW server lifecycle is handled globally in `src/test/setup.ts`. Individual tests add handlers via `server.use(...)`.

## WireMock vs MSW Comparison

| Aspect | Backend (WireMock) | Frontend (MSW) |
|--------|-------------------|----------------|
| Setup | `new WireMockServer(port)` | `setupServer()` |
| Stub | `stubFor(post(...).willReturn(...))` | `server.use(http.post(...))` |
| Cleanup | `wireMockServer.stop()` | `server.close()` |
| Reset | N/A | `server.resetHandlers()` |

## Test Verification

```
Skill tool: skill="test-frontend", args="{feature}.api"
```
