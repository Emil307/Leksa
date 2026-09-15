import { describe, it, expect } from 'vitest';
import type { EmailScreenView } from '../../types';
import { EMAIL, emailScreen, emailSendingScreen } from '@/test/shared/auth';
import { buildChallengeStartRequest, selectEmailScreenView, validateEmail } from '../main/email.logic';

const LONGEST_VALID_EMAIL = `${'a'.repeat(249)}@x.io`;
const TOO_LONG_EMAIL = `${'a'.repeat(250)}@x.io`;

const idle = (email: string) => emailScreen({ email });

const idleView = (email: string, requestEnabled: boolean): EmailScreenView => ({
  email,
  inputEnabled: true,
  requestEnabled,
  requestButton: 'request',
  fieldTone: 'normal',
  message: null,
});

describe('Логика почты', () => {
  describe('validateEmail', () => {
    it('сообщает empty для пустого адреса', () => {
      expect(validateEmail('')).toBe('empty');
    });

    it('сообщает malformed без знака @', () => {
      expect(validateEmail('user.example.com')).toBe('malformed');
    });

    it('сообщает malformed без домена', () => {
      expect(validateEmail('user@')).toBe('malformed');
    });

    it('сообщает malformed без локальной части', () => {
      expect(validateEmail('@example.com')).toBe('malformed');
    });

    it('сообщает malformed при пробеле внутри', () => {
      expect(validateEmail('us er@example.com')).toBe('malformed');
    });

    it('сообщает malformed без точки в домене', () => {
      expect(validateEmail('user@localhost')).toBe('malformed');
    });

    it('сообщает too-long свыше 254 октетов', () => {
      expect(validateEmail(TOO_LONG_EMAIL)).toBe('too-long');
    });

    it('считает октеты, а не символы, для лимита длины', () => {
      expect(validateEmail(`${'ё'.repeat(125)}@x.io`)).toBe('too-long');
    });

    it('сообщает valid ровно при 254 октетах', () => {
      expect(validateEmail(LONGEST_VALID_EMAIL)).toBe('valid');
    });

    it('сообщает valid для обычного адреса', () => {
      expect(validateEmail(EMAIL)).toBe('valid');
    });

    it('сообщает valid для адреса с плюсом и поддоменом', () => {
      expect(validateEmail('first.last+tag@mail.example.co.uk')).toBe('valid');
    });
  });

  describe('buildChallengeStartRequest', () => {
    it('собирает запрос запуска с типом проверки по коду из письма', () => {
      expect(buildChallengeStartRequest(EMAIL)).toStrictEqual({
        email: EMAIL,
        challengeType: 'EMAIL_CODE',
      });
    });
  });

  describe('selectEmailScreenView', () => {
    it('выключает кнопку запроса для пустого адреса', () => {
      expect(selectEmailScreenView(idle(''))).toStrictEqual(idleView('', false));
    });

    it('выключает кнопку запроса для искажённого адреса', () => {
      expect(selectEmailScreenView(idle('user@'))).toStrictEqual(idleView('user@', false));
    });

    it('выключает кнопку запроса для слишком длинного адреса', () => {
      expect(selectEmailScreenView(idle(TOO_LONG_EMAIL))).toStrictEqual(idleView(TOO_LONG_EMAIL, false));
    });

    it('включает кнопку запроса для верного адреса', () => {
      expect(selectEmailScreenView(idle(EMAIL))).toStrictEqual(idleView(EMAIL, true));
    });

    it('блокирует экран, пока запрос кода в пути', () => {
      expect(selectEmailScreenView(emailSendingScreen())).toStrictEqual({
        email: EMAIL,
        inputEnabled: false,
        requestEnabled: false,
        requestButton: 'sending',
        fieldTone: 'disabled',
        message: null,
      });
    });
  });
});
