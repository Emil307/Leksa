import { describe, it, expect } from 'vitest';
import {
  EMAIL,
  EXPIRES_AT_EPOCH_MS,
  REQUESTED_AT_EPOCH_MS,
  SESSION,
  codeFilledScreen,
  codeScreen,
  codeSubmittingScreen,
  emailScreen,
  emailSendingScreen,
  onCodeScreen,
  onEmailScreen,
  startedOutcome,
} from '@/test/shared/auth';
import { authReducer, createInitialAuthState, nextRequestId } from '../main/auth.reducer';

const emailIdle = onEmailScreen(emailScreen());
const emailSending = onEmailScreen(emailSendingScreen());
const codeWaiting = onCodeScreen(codeScreen());
const codeFilled = onCodeScreen(codeFilledScreen());
const codeSubmitting = onCodeScreen(codeSubmittingScreen());

const codeRequested = (requestId: number) =>
  ({ type: 'code-requested', requestId, outcome: startedOutcome, nowEpochMs: REQUESTED_AT_EPOCH_MS }) as const;

const codeVerified = (requestId: number) =>
  ({ type: 'code-verified', requestId, outcome: { kind: 'signed-in', session: SESSION } }) as const;

describe('Редьюсер входа', () => {
  describe('createInitialAuthState', () => {
    it('начинает с экрана почты и пустого адреса', () => {
      expect(createInitialAuthState()).toStrictEqual(onEmailScreen(emailScreen({ email: '' })));
    });
  });

  describe('nextRequestId', () => {
    it('начинает с единицы, когда ничего не ожидается', () => {
      expect(nextRequestId(emailIdle)).toBe(1);
    });

    it('продолжает id ожидающего запроса', () => {
      expect(nextRequestId(emailSending)).toBe(2);
    });

    it('начинает с единицы на экране кода, когда ничего не ожидается', () => {
      expect(nextRequestId(codeWaiting)).toBe(1);
    });

    it('продолжает id ожидающей проверки на экране кода', () => {
      expect(nextRequestId(codeSubmitting)).toBe(2);
    });
  });

  describe('экран почты', () => {
    it('сохраняет введённый адрес', () => {
      expect(authReducer(createInitialAuthState(), { type: 'email-changed', email: EMAIL })).toStrictEqual(emailIdle);
    });

    it('помечает запрос кода ожидающим', () => {
      expect(authReducer(emailIdle, { type: 'request-code', requestId: 1 })).toStrictEqual(emailSending);
    });

    it('игнорирует второй запрос, пока первый в пути', () => {
      expect(authReducer(emailSending, { type: 'request-code', requestId: 2 })).toStrictEqual(emailSending);
    });

    it('переходит на экран кода, когда ожидаемый запрос завершается успехом', () => {
      expect(authReducer(emailSending, codeRequested(1))).toStrictEqual(codeWaiting);
    });

    it('отбрасывает ответ с чужим id запроса', () => {
      expect(authReducer(emailSending, codeRequested(2))).toStrictEqual(emailSending);
    });

    it('отбрасывает запоздалый ответ, когда ничего не ожидается', () => {
      expect(authReducer(emailIdle, codeRequested(1))).toStrictEqual(emailIdle);
    });
  });

  describe('экран кода', () => {
    it('вводит цифру и сдвигает фокус', () => {
      expect(authReducer(codeWaiting, { type: 'cell-input', index: 0, value: '4' })).toStrictEqual(
        onCodeScreen(codeScreen({ cells: ['4', '', '', '', '', ''], focusedCell: 1 }))
      );
    });

    it('стирает назад по backspace', () => {
      expect(authReducer(codeFilled, { type: 'cell-backspace', index: 5 })).toStrictEqual(
        onCodeScreen(codeFilledScreen({ cells: ['0', '1', '2', '3', '4', ''] }))
      );
    });

    it('помечает проверку ожидающей при подтверждении', () => {
      expect(authReducer(codeFilled, { type: 'confirm-code', requestId: 1 })).toStrictEqual(codeSubmitting);
    });

    it('игнорирует второе подтверждение, пока первое в пути', () => {
      expect(authReducer(codeSubmitting, { type: 'confirm-code', requestId: 2 })).toStrictEqual(codeSubmitting);
    });

    it('входит, держа сессию только в памяти', () => {
      expect(authReducer(codeSubmitting, codeVerified(1))).toStrictEqual({ screen: 'signed-in', session: SESSION });
    });

    it('отбрасывает результат проверки с чужим id запроса', () => {
      expect(authReducer(codeSubmitting, codeVerified(2))).toStrictEqual(codeSubmitting);
    });

    it('отбрасывает запоздалый результат проверки, когда ничего не ожидается', () => {
      expect(authReducer(codeFilled, codeVerified(1))).toStrictEqual(codeFilled);
    });

    it('возвращается на экран почты с сохранённым адресом при смене почты', () => {
      expect(authReducer(codeFilled, { type: 'change-email' })).toStrictEqual(emailIdle);
    });

    it('уменьшает отсчёт по тику', () => {
      expect(authReducer(codeWaiting, { type: 'tick', nowEpochMs: EXPIRES_AT_EPOCH_MS - 61000 })).toStrictEqual(
        onCodeScreen(codeScreen({ secondsLeft: 61 }))
      );
    });

    it('истекает на нуле', () => {
      expect(authReducer(codeWaiting, { type: 'tick', nowEpochMs: EXPIRES_AT_EPOCH_MS })).toStrictEqual(
        onCodeScreen(codeScreen({ secondsLeft: 0, status: 'expired' }))
      );
    });

    it('игнорирует тик на экране почты', () => {
      expect(authReducer(emailIdle, { type: 'tick', nowEpochMs: EXPIRES_AT_EPOCH_MS })).toStrictEqual(emailIdle);
    });
  });
});
