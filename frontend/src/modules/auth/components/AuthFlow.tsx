import { useEffect, useReducer } from 'react';
import type { AuthFlowProps, TickIntervalMs } from '@/modules/auth/types';
import { authReducer, createInitialAuthState, nextRequestId } from '@/modules/auth/logic/main/auth.reducer';
import { buildChallengeStartRequest, selectEmailScreenView } from '@/modules/auth/logic/main/email.logic';
import { buildChallengeVerifyRequest, selectCodeScreenView } from '@/modules/auth/logic/main/code.logic';
import { AuthShell } from './AuthShell';
import { CodeScreen } from './CodeScreen';
import { EmailScreen } from './EmailScreen';
import { SignedInScreen } from './SignedInScreen';

const TICK_INTERVAL_MS: TickIntervalMs = 1000;

export function AuthFlow({ client, now = Date.now }: AuthFlowProps) {
  const [state, dispatch] = useReducer(authReducer, undefined, createInitialAuthState);

  useEffect(() => {
    const timer = setInterval(() => dispatch({ type: 'tick', nowEpochMs: now() }), TICK_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [now]);

  const requestCode = async () => {
    if (state.screen !== 'email') return;
    const requestId = nextRequestId(state);
    dispatch({ type: 'request-code', requestId });
    const outcome = await client.startChallenge(buildChallengeStartRequest(state.email.email));
    dispatch({ type: 'code-requested', requestId, outcome, nowEpochMs: now() });
  };

  const confirmCode = async () => {
    if (state.screen !== 'code') return;
    const requestId = nextRequestId(state);
    dispatch({ type: 'confirm-code', requestId });
    const outcome = await client.verifyChallenge(buildChallengeVerifyRequest(state.code.challengeId, state.code.cells));
    dispatch({ type: 'code-verified', requestId, outcome });
  };

  const resendCode = async () => {
    if (state.screen !== 'code') return;
    const requestId = nextRequestId(state);
    dispatch({ type: 'resend-code', requestId });
    const outcome = await client.startChallenge(buildChallengeStartRequest(state.code.email));
    dispatch({ type: 'code-resent', requestId, outcome, nowEpochMs: now() });
  };

  return (
    <AuthShell>
      {state.screen === 'email' && (
        <EmailScreen
          view={selectEmailScreenView(state.email)}
          onEmailChange={(email) => dispatch({ type: 'email-changed', email })}
          onRequestCode={() => void requestCode()}
        />
      )}
      {state.screen === 'code' && (
        <CodeScreen
          view={selectCodeScreenView(state.code)}
          onCellInput={(index, value) => dispatch({ type: 'cell-input', index, value })}
          onCellBackspace={(index) => dispatch({ type: 'cell-backspace', index })}
          onConfirm={() => void confirmCode()}
          onResend={() => void resendCode()}
          onChangeEmail={() => dispatch({ type: 'change-email' })}
        />
      )}
      {state.screen === 'signed-in' && <SignedInScreen />}
    </AuthShell>
  );
}
