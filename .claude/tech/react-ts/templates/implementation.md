# Frontend Implementation Template

## Logic Implementation (.logic.ts)

```typescript
export function validateEmail(email: string): ValidationResult {
  if (!email) return { valid: false, error: 'Email is required' }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return { valid: false, error: 'Invalid email format' }
  return { valid: true }
}

export function isFormValid(state: RegistrationFormState): boolean {
  return validateEmail(state.email).valid
    && validatePassword(state.password).valid
    && state.password === state.confirmPassword
}

export function buildRegistrationRequest(state: RegistrationFormState): RegistrationRequest {
  return { email: state.email, password: state.password, passwordConfirmation: state.confirmPassword }
}
```

## API Client Implementation (api/)

Transport and the whole error protocol (status → `ApiError` mapping, retry hint on 409,
refresh on 401) live in `@/shared/api`; the feature `api/` folder mirrors the backend REST
adapter — a client class that only delegates, one endpoint per operation, and DTO classes
that read the success wire shape. Endpoints never look at error responses.

`api/main/dto/registration-response.dto.ts`:

```typescript
import { isJsonObject, isString } from '@/shared/utils'
import type { RegisteredUser } from '../../types'

export class RegistrationResponseDto {
  private constructor(readonly userId: string) {}

  static parse(body: unknown): RegistrationResponseDto | null {
    if (!isJsonObject(body) || !isString(body.userId)) return null
    return new RegistrationResponseDto(body.userId)
  }

  toRegisteredUser(): RegisteredUser {
    return { userId: this.userId }
  }
}
```

`api/main/endpoints/register.endpoint.ts`:

```typescript
import type { ApiEndpoint } from '@/shared/api'
import type { RegistrationSuccess } from '../../types'
import { RegistrationResponseDto } from '../dto/registration-response.dto'

export const registerEndpoint: ApiEndpoint<RegistrationSuccess> = {
  path: '/api/v1/auth/register',
  parse: (body) => {
    const registered = RegistrationResponseDto.parse(body)
    return registered ? { kind: 'registered', user: registered.toRegisteredUser() } : null
  },
}
```

`api/main/registration.api.ts`:

```typescript
import { apiClient, type ApiClient } from '@/shared/api'
import type { RegistrationApiClient, RegistrationOutcome, RegistrationRequest } from '../types'
import { registerEndpoint } from './endpoints/register.endpoint'

export class RegistrationApi implements RegistrationApiClient {
  constructor(private readonly api: ApiClient) {}

  registerUser = (request: RegistrationRequest): Promise<RegistrationOutcome> =>
    this.api.call(registerEndpoint, request)
}

export const registrationApi = new RegistrationApi(apiClient)
```

The outcome type in `types/` is `ApiOutcome<RegistrationSuccess>` = `RegistrationSuccess |
ApiError`; a taken email arrives as `{ kind: 'conflict' }` from the shared mapper and the
feature's `logic/` turns it into a screen state — no feature ever declares `email-taken`.

## Humble Object Component (.tsx)

Build AFTER logic and API are tested. Components live in `components/` subdirectory.

Page component (`components/{Feature}Page.tsx`) — orchestrates state and composes field components:

```tsx
import { useState } from 'react'
import { validateEmail, buildRegistrationRequest } from '../logic/main/registration.logic'
import { registrationApi } from '../api/main/registration.api'
import { EmailField } from './EmailField'
import type { RegistrationFormState } from '../types'

export function RegistrationPage() {
  const [form, setForm] = useState<RegistrationFormState>(getInitialFormState)
  const [isLoading, setIsLoading] = useState(false)

  const updateField = (field: keyof RegistrationFormState, value: string | boolean) => {
    setForm(prev => ({ ...prev, [field]: value }))
  }

  const submitForm = async () => {
    if (isLoading) return
    setIsLoading(true)
    await registrationApi.registerUser(buildRegistrationRequest(form)).catch(() => {})
  }

  return (
    <form onSubmit={handleSubmit}>
      <EmailField value={form.email} onChange={v => updateField('email', v)} />
      {/* ... other field components ... */}
    </form>
  )
}
```

Field components (`components/{FieldName}.tsx`) — encapsulate label + input + error for one field:

```tsx
export function EmailField({ value, error, onChange, onBlur }: EmailFieldProps) {
  return (
    <div>
      <label htmlFor="email">Email</label>
      <input data-testid="email-input" value={value} onChange={e => onChange(e.target.value)} onBlur={onBlur} />
      {error && <FieldError message={error} />}
    </div>
  )
}
```

## Test Verification

```
Skill tool: skill="test-frontend", args="{feature}"
```
