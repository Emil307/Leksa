import type { ChallengeStartRequest, ChallengeStartResponse, ChallengeVerifyRequest } from './challengeApi.types';
import type { AuthSession } from './session.types';
import type { ApiOutcome } from '@/shared/api';

export interface ChallengeStarted {
  kind: 'started';
  challenge: ChallengeStartResponse;
}

export interface ChallengeSignedIn {
  kind: 'signed-in';
  session: AuthSession;
}

export type ChallengeStartOutcome = ApiOutcome<ChallengeStarted>;

export type ChallengeVerifyOutcome = ApiOutcome<ChallengeSignedIn>;

export type StartChallenge = (request: ChallengeStartRequest) => Promise<ChallengeStartOutcome>;

export type VerifyChallenge = (request: ChallengeVerifyRequest) => Promise<ChallengeVerifyOutcome>;

export interface ChallengeApiClient {
  startChallenge: StartChallenge;
  verifyChallenge: VerifyChallenge;
}
