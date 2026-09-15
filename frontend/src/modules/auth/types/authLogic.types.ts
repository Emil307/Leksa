import type { ChallengeStartRequest, ChallengeVerifyRequest } from './challengeApi.types';
import type {
  CodeCellIndex,
  CodeCells,
  CodeCellsTransition,
  CodeScreenState,
  CodeScreenView,
} from './codeScreen.types';
import type { EmailScreenState, EmailScreenView, EmailValidity } from './emailScreen.types';

export type ValidateEmail = (email: string) => EmailValidity;

export type BuildChallengeStartRequest = (email: string) => ChallengeStartRequest;

export type BuildChallengeVerifyRequest = (challengeId: string, cells: CodeCells) => ChallengeVerifyRequest;

export type JoinCode = (cells: CodeCells) => string;

export type IsCodeComplete = (cells: CodeCells) => boolean;

export type CreateEmptyCells = () => CodeCells;

export type EnterCellDigit = (cells: CodeCells, index: CodeCellIndex, value: string) => CodeCellsTransition;

export type ClearCellBackwards = (cells: CodeCells, index: CodeCellIndex) => CodeCellsTransition;

export type ParseExpiresAt = (expiresAt: string) => number;

export type ComputeSecondsLeft = (expiresAtEpochMs: number, nowEpochMs: number) => number;

export type FormatCountdown = (seconds: number) => string;

export type SelectEmailScreenView = (state: EmailScreenState) => EmailScreenView;

export type SelectCodeScreenView = (state: CodeScreenState) => CodeScreenView;

export type TickIntervalMs = 1000;
