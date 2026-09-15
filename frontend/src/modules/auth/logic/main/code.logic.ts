import type {
  BuildChallengeVerifyRequest,
  ClearCellBackwards,
  CodeCellIndex,
  CodeCells,
  CodeCellsTone,
  CodeScreenMessage,
  CodeScreenState,
  CodeScreenStatus,
  ConfirmButtonMode,
  CreateEmptyCells,
  EnterCellDigit,
  IsCodeComplete,
  JoinCode,
  SelectCodeScreenView,
} from '../../types';
import { formatCountdown } from './countdown.logic';

const LAST_CELL: CodeCellIndex = 5;
const ASCII_DIGIT = /^[0-9]$/;

const replaceCell = (cells: CodeCells, index: CodeCellIndex, value: string): CodeCells =>
  cells.map((cell, position) => (position === index ? value : cell)) as unknown as CodeCells;

export const createEmptyCells: CreateEmptyCells = () => ['', '', '', '', '', ''];

export const enterCellDigit: EnterCellDigit = (cells, index, value) => {
  if (!ASCII_DIGIT.test(value)) return { cells, focusedCell: index };
  const focusedCell = Math.min(index + 1, LAST_CELL) as CodeCellIndex;
  return { cells: replaceCell(cells, index, value), focusedCell };
};

export const clearCellBackwards: ClearCellBackwards = (cells, index) => {
  if (cells[index] !== '') return { cells: replaceCell(cells, index, ''), focusedCell: index };
  if (index === 0) return { cells, focusedCell: index };
  const previous = (index - 1) as CodeCellIndex;
  return { cells: replaceCell(cells, previous, ''), focusedCell: previous };
};

export const joinCode: JoinCode = (cells) => cells.join('');

export const isCodeComplete: IsCodeComplete = (cells) => cells.every((cell) => cell !== '');

export const buildChallengeVerifyRequest: BuildChallengeVerifyRequest = (challengeId, cells) => ({
  challengeId,
  code: joinCode(cells),
});

const selectMessage = (state: CodeScreenState): CodeScreenMessage | null => {
  switch (state.status) {
    case 'rejected':
      return { kind: 'code-rejected', secondsLeft: null };
    case 'expired':
      return { kind: 'code-expired', secondsLeft: null };
    case 'unavailable':
      return { kind: 'unavailable', secondsLeft: null };
    default:
      return state.resendCooldownSecondsLeft === null
        ? null
        : { kind: 'resend-cooldown', secondsLeft: state.resendCooldownSecondsLeft };
  }
};

const selectCellsTone = (status: CodeScreenStatus): CodeCellsTone => {
  switch (status) {
    case 'submitting':
    case 'expired':
      return 'disabled';
    case 'rejected':
      return 'error';
    default:
      return 'normal';
  }
};

const selectConfirmButton = (status: CodeScreenStatus): ConfirmButtonMode => {
  switch (status) {
    case 'submitting':
      return 'verifying';
    case 'unavailable':
      return 'retry';
    default:
      return 'confirm';
  }
};

export const selectCodeScreenView: SelectCodeScreenView = (state) => {
  const submitting = state.status === 'submitting';
  const expired = state.status === 'expired';
  const cellsEnabled = !submitting && !expired;
  return {
    email: state.email,
    countdown: formatCountdown(state.secondsLeft),
    expired,
    cells: state.cells,
    focusedCell: state.focusedCell,
    cellsEnabled,
    cellsTone: selectCellsTone(state.status),
    confirmEnabled: cellsEnabled && isCodeComplete(state.cells),
    confirmButton: selectConfirmButton(state.status),
    resend: {
      enabled: !submitting && state.resendCooldownSecondsLeft === null,
      cooldownSecondsLeft: state.resendCooldownSecondsLeft,
    },
    changeEmailEnabled: !submitting,
    message: selectMessage(state),
  };
};
