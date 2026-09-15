import { afterAll, afterEach, beforeAll } from 'vitest';
import { server } from './shared/mswServer';

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
