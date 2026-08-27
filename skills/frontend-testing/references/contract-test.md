# Consumer-driven contract testing (rule 13)

Pact defines the API contract from the *frontend consumer's* perspective and
verifies it against the *backend provider*, catching integration mismatches
before they reach production. This file is the **consumer** side (what the
frontend owns). The provider verifies the published pact separately.

## Install

```bash
npm i -D @pact-foundation/pact
```

## Consumer example

```ts
// tests/contract/user-api.contract.test.ts
import { Pact } from '@pact-foundation/pact';
import { like } from '@pact-foundation/pact/dsl/matchers';
import path from 'node:path';

const provider = new Pact({
  consumer: 'web-frontend',
  provider: 'users-api',
  port: 3001,
  dir: path.resolve(process.cwd(), 'pacts'),
  logLevel: 'warn',
});

describe('User API contract', () => {
  beforeAll(() => provider.setup());
  afterAll(() => provider.finalize());

  it('returns a user profile the frontend expects', async () => {
    await provider.addInteraction({
      uponReceiving: 'a request for user 42',
      withRequest: {
        method: 'GET',
        path: '/users/42',
        headers: { Accept: 'application/json' },
      },
      willRespondWith: {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        body: like({ id: 42, name: 'Ada', email: 'ada@example.com' }),
      },
    });

    const res = await fetch('http://localhost:3001/users/42');
    const user = await res.json();
    expect(user.id).toBe(42);
    expect(user.name).toBeDefined();
    expect(user.email).toMatch(/.+@.+/);
  });
});
```

## How it fits the pipeline

1. The consumer test runs in CI, generates `pacts/web-frontend-users-api.json`.
2. Publish it to a Pact Broker (`npx pact publish`) or hand it to the backend
   team.
3. The **provider** runs `@pact-foundation/pact` verification against its running
   service; if the contract breaks, the backend build fails *before* it ships —
   so the frontend never sees a silent API regression.

## Notes

- `like(...)` means "match this shape" — the provider may return other fields,
  but the ones you assert must be present and typed.
- Keep contracts to the fields the UI actually consumes. Over-asserting makes the
  contract brittle.
- This is the frontend's boundary guard; it does not replace E2E, which still
  proves the full journey against a real deployed backend in staging.
