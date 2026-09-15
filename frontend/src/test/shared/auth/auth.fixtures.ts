import type { AuthSession, ChallengeStartOutcome, CodeCells } from '@/modules/auth/types';

export const EMAIL = 'user@example.com';
export const CHALLENGE_ID = 'ch-1';
export const EXPIRES_AT = '2026-09-14T12:05:00Z';
export const EXPIRES_AT_EPOCH_MS = 1789387500000;
export const CHALLENGE_LIFETIME_MS = 300000;
export const REQUESTED_AT_EPOCH_MS = EXPIRES_AT_EPOCH_MS - CHALLENGE_LIFETIME_MS;

export const EMPTY_CELLS: CodeCells = ['', '', '', '', '', ''];
export const FULL_CELLS: CodeCells = ['0', '1', '2', '3', '4', '5'];
export const PARTIAL_CELLS: CodeCells = ['0', '1', '2', '', '', ''];
export const FULL_CODE = '012345';

export const SESSION: AuthSession = {
  userId: 'user-1',
  sessionId: 'session-1',
  accessToken: 'access-1',
  refreshToken: 'refresh-1',
};

export const startedOutcome: ChallengeStartOutcome = {
  kind: 'started',
  challenge: { challengeId: CHALLENGE_ID, challengeType: 'EMAIL_CODE', expiresAt: EXPIRES_AT },
};
