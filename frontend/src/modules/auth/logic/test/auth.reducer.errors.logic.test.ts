import { describe, it, expect } from 'vitest';
import type { ChallengeStartOutcome, ChallengeVerifyOutcome } from '../../types';
import {
  codeFilledScreen,
  codeSubmittingScreen,
  emailScreen,
  emailSendingScreen,
  onCodeScreen,
  onEmailScreen,
} from '@/test/shared/auth';
import { authReducer } from '../main/auth.reducer';

const failedStart = (outcome: ChallengeStartOutcome) =>
  authReducer(onEmailScreen(emailSendingScreen()), { type: 'code-requested', requestId: 1, outcome, nowEpochMs: 0 });

const failedVerify = (outcome: ChallengeVerifyOutcome) =>
  authReducer(onCodeScreen(codeSubmittingScreen()), { type: 'code-verified', requestId: 1, outcome });

const failedResend = (outcome: ChallengeStartOutcome) =>
  authReducer(onCodeScreen(codeFilledScreen({ pendingRequestId: 1 })), {
    type: 'code-resent',
    requestId: 1,
    outcome,
    nowEpochMs: 0,
  });

describe('Редьюсер входа при ошибках API', () => {
  it('помечает адрес неверным при validation-failed', () => {
    expect(failedStart({ kind: 'validation-failed' })).toStrictEqual(onEmailScreen(emailScreen({ status: 'invalid' })));
  });

  it('закрывает кнопку на секунды, названные в конфликте', () => {
    expect(failedStart({ kind: 'conflict', retryAfterSeconds: 42 })).toStrictEqual(
      onEmailScreen(emailScreen({ status: 'cooldown', cooldownSecondsLeft: 42 }))
    );
  });

  it('считает конфликт без подсказки о повторе недоступностью', () => {
    expect(failedStart({ kind: 'conflict', retryAfterSeconds: null })).toStrictEqual(
      onEmailScreen(emailScreen({ status: 'unavailable' }))
    );
  });

  it.each<ChallengeStartOutcome>([{ kind: 'unavailable' }, { kind: 'unexpected', status: 500 }])(
    'сообщает о недоступности сервиса при %o',
    (outcome) => {
      expect(failedStart(outcome)).toStrictEqual(onEmailScreen(emailScreen({ status: 'unavailable' })));
    }
  );

  it.each<ChallengeVerifyOutcome>([{ kind: 'unauthorized' }, { kind: 'validation-failed' }])(
    'отклоняет код при %o, сохраняя ячейки',
    (outcome) => {
      expect(failedVerify(outcome)).toStrictEqual(onCodeScreen(codeFilledScreen({ status: 'rejected' })));
    }
  );

  it('помечает проверку недоступной при любой другой ошибке', () => {
    expect(failedVerify({ kind: 'unavailable' })).toStrictEqual(
      onCodeScreen(codeFilledScreen({ status: 'unavailable' }))
    );
  });

  it('закрывает повторную отправку на секунды, названные в конфликте', () => {
    expect(failedResend({ kind: 'conflict', retryAfterSeconds: 30 })).toStrictEqual(
      onCodeScreen(codeFilledScreen({ resendCooldownSecondsLeft: 30 }))
    );
  });

  it('помечает повторную отправку недоступной при любой другой ошибке', () => {
    expect(failedResend({ kind: 'unexpected', status: 500 })).toStrictEqual(
      onCodeScreen(codeFilledScreen({ status: 'unavailable' }))
    );
  });
});
