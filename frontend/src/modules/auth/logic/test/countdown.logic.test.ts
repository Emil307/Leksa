import { describe, it, expect } from 'vitest';
import { EXPIRES_AT, EXPIRES_AT_EPOCH_MS } from '@/test/shared/auth';
import { computeSecondsLeft, formatCountdown, parseExpiresAt } from '../main/countdown.logic';

describe('Логика обратного отсчёта', () => {
  describe('parseExpiresAt', () => {
    it('разбирает UTC-метку с суффиксом Z', () => {
      expect(parseExpiresAt(EXPIRES_AT)).toBe(EXPIRES_AT_EPOCH_MS);
    });

    it('разбирает метку с положительным смещением в тот же момент', () => {
      expect(parseExpiresAt('2026-09-14T21:05:00+09:00')).toBe(EXPIRES_AT_EPOCH_MS);
    });

    it('разбирает метку с отрицательным смещением в тот же момент', () => {
      expect(parseExpiresAt('2026-09-14T07:05:00-05:00')).toBe(EXPIRES_AT_EPOCH_MS);
    });

    it('разбирает метку с долями секунды', () => {
      expect(parseExpiresAt('2026-09-14T12:05:00.250Z')).toBe(EXPIRES_AT_EPOCH_MS + 250);
    });
  });

  describe('computeSecondsLeft', () => {
    it('возвращает целые секунды до истечения', () => {
      expect(computeSecondsLeft(EXPIRES_AT_EPOCH_MS, EXPIRES_AT_EPOCH_MS - 300000)).toBe(300);
    });

    it('округляет неполную секунду вверх', () => {
      expect(computeSecondsLeft(EXPIRES_AT_EPOCH_MS, EXPIRES_AT_EPOCH_MS - 299500)).toBe(300);
    });

    it('возвращает ноль в момент истечения', () => {
      expect(computeSecondsLeft(EXPIRES_AT_EPOCH_MS, EXPIRES_AT_EPOCH_MS)).toBe(0);
    });

    it('не опускается ниже нуля после истечения', () => {
      expect(computeSecondsLeft(EXPIRES_AT_EPOCH_MS, EXPIRES_AT_EPOCH_MS + 15000)).toBe(0);
    });
  });

  describe('formatCountdown', () => {
    it('форматирует пять минут как 5:00', () => {
      expect(formatCountdown(300)).toBe('5:00');
    });

    it('дополняет секунды меньше десяти нулём', () => {
      expect(formatCountdown(61)).toBe('1:01');
    });

    it('форматирует ноль как 0:00', () => {
      expect(formatCountdown(0)).toBe('0:00');
    });

    it('форматирует одни секунды с нулевой минутой', () => {
      expect(formatCountdown(9)).toBe('0:09');
    });

    it('форматирует последнюю секунду минуты', () => {
      expect(formatCountdown(119)).toBe('1:59');
    });
  });
});
