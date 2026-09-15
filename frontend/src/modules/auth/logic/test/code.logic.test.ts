import { describe, it, expect } from 'vitest';
import type { CodeCells, CodeScreenView } from '../../types';
import { CHALLENGE_ID, EMAIL, EMPTY_CELLS, FULL_CELLS, FULL_CODE, PARTIAL_CELLS, codeScreen } from '@/test/shared/auth';
import {
  buildChallengeVerifyRequest,
  clearCellBackwards,
  createEmptyCells,
  enterCellDigit,
  isCodeComplete,
  joinCode,
  selectCodeScreenView,
} from '../main/code.logic';

const waiting = (cells: CodeCells, secondsLeft: number) => codeScreen({ cells, secondsLeft });

const waitingView = (cells: CodeCells, countdown: string, confirmEnabled: boolean): CodeScreenView => ({
  email: EMAIL,
  countdown,
  expired: false,
  cells,
  focusedCell: 0,
  cellsEnabled: true,
  cellsTone: 'normal',
  confirmEnabled,
  confirmButton: 'confirm',
  resend: { enabled: true, cooldownSecondsLeft: null },
  changeEmailEnabled: true,
  message: null,
});

describe('Логика кода', () => {
  describe('createEmptyCells', () => {
    it('создаёт шесть пустых ячеек', () => {
      expect(createEmptyCells()).toStrictEqual(EMPTY_CELLS);
    });
  });

  describe('enterCellDigit', () => {
    it('сохраняет ASCII-цифру и сдвигает фокус', () => {
      expect(enterCellDigit(EMPTY_CELLS, 0, '7')).toStrictEqual({ cells: ['7', '', '', '', '', ''], focusedCell: 1 });
    });

    it('оставляет фокус на последней ячейке', () => {
      expect(enterCellDigit(PARTIAL_CELLS, 5, '9')).toStrictEqual({
        cells: ['0', '1', '2', '', '', '9'],
        focusedCell: 5,
      });
    });

    it('перезаписывает заполненную ячейку', () => {
      expect(enterCellDigit(FULL_CELLS, 2, '8')).toStrictEqual({
        cells: ['0', '1', '8', '3', '4', '5'],
        focusedCell: 3,
      });
    });

    it('отклоняет букву, не сдвигая фокус', () => {
      expect(enterCellDigit(EMPTY_CELLS, 1, 'a')).toStrictEqual({ cells: EMPTY_CELLS, focusedCell: 1 });
    });

    it('отклоняет не-ASCII цифру', () => {
      expect(enterCellDigit(EMPTY_CELLS, 0, '７')).toStrictEqual({ cells: EMPTY_CELLS, focusedCell: 0 });
    });

    it('отклоняет пустое значение', () => {
      expect(enterCellDigit(PARTIAL_CELLS, 3, '')).toStrictEqual({ cells: PARTIAL_CELLS, focusedCell: 3 });
    });

    it('отклоняет больше одного символа', () => {
      expect(enterCellDigit(EMPTY_CELLS, 0, '12')).toStrictEqual({ cells: EMPTY_CELLS, focusedCell: 0 });
    });
  });

  describe('clearCellBackwards', () => {
    it('очищает заполненную ячейку и оставляет фокус на ней', () => {
      expect(clearCellBackwards(PARTIAL_CELLS, 2)).toStrictEqual({ cells: ['0', '1', '', '', '', ''], focusedCell: 2 });
    });

    it('отступает из пустой ячейки и очищает предыдущую', () => {
      expect(clearCellBackwards(PARTIAL_CELLS, 3)).toStrictEqual({ cells: ['0', '1', '', '', '', ''], focusedCell: 2 });
    });

    it('остаётся на первой ячейке, если она пуста', () => {
      expect(clearCellBackwards(EMPTY_CELLS, 0)).toStrictEqual({ cells: EMPTY_CELLS, focusedCell: 0 });
    });
  });

  describe('joinCode', () => {
    it('сохраняет ведущий ноль', () => {
      expect(joinCode(FULL_CELLS)).toBe(FULL_CODE);
    });

    it('склеивает частично заполненные ячейки без заглушек', () => {
      expect(joinCode(PARTIAL_CELLS)).toBe('012');
    });
  });

  describe('isCodeComplete', () => {
    it('полон при шести цифрах', () => {
      expect(isCodeComplete(FULL_CELLS)).toBe(true);
    });

    it('неполон при пустой ячейке', () => {
      expect(isCodeComplete(['0', '1', '2', '3', '', '5'])).toBe(false);
    });

    it('неполон без цифр', () => {
      expect(isCodeComplete(EMPTY_CELLS)).toBe(false);
    });
  });

  describe('buildChallengeVerifyRequest', () => {
    it('отправляет id проверки и код строкой', () => {
      const request = buildChallengeVerifyRequest(CHALLENGE_ID, FULL_CELLS);

      expect(request).toStrictEqual({ challengeId: CHALLENGE_ID, code: FULL_CODE });
      expect(typeof request.code).toBe('string');
    });
  });

  describe('selectCodeScreenView', () => {
    it('показывает свежий экран кода с выключенным подтверждением', () => {
      expect(selectCodeScreenView(waiting(EMPTY_CELLS, 300))).toStrictEqual(waitingView(EMPTY_CELLS, '5:00', false));
    });

    it('держит подтверждение выключенным при частичном коде', () => {
      expect(selectCodeScreenView(waiting(PARTIAL_CELLS, 61))).toStrictEqual(waitingView(PARTIAL_CELLS, '1:01', false));
    });

    it('включает подтверждение при полном коде', () => {
      expect(selectCodeScreenView(waiting(FULL_CELLS, 299))).toStrictEqual(waitingView(FULL_CELLS, '4:59', true));
    });

    it('блокирует всё, пока код проверяется', () => {
      expect(
        selectCodeScreenView({ ...waiting(FULL_CELLS, 250), status: 'submitting', pendingRequestId: 1 })
      ).toStrictEqual({
        email: EMAIL,
        countdown: '4:10',
        expired: false,
        cells: FULL_CELLS,
        focusedCell: 0,
        cellsEnabled: false,
        cellsTone: 'disabled',
        confirmEnabled: false,
        confirmButton: 'verifying',
        resend: { enabled: false, cooldownSecondsLeft: null },
        changeEmailEnabled: false,
        message: null,
      });
    });

    it('закрывает ячейки и предлагает повторную отправку после истечения кода', () => {
      expect(selectCodeScreenView({ ...waiting(PARTIAL_CELLS, 0), status: 'expired' })).toStrictEqual({
        email: EMAIL,
        countdown: '0:00',
        expired: true,
        cells: PARTIAL_CELLS,
        focusedCell: 0,
        cellsEnabled: false,
        cellsTone: 'disabled',
        confirmEnabled: false,
        confirmButton: 'confirm',
        resend: { enabled: true, cooldownSecondsLeft: null },
        changeEmailEnabled: true,
        message: { kind: 'code-expired', secondsLeft: null },
      });
    });
  });
});
