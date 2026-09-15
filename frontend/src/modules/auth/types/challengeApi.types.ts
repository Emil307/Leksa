export type ChallengeType = 'EMAIL_CODE';

export interface ChallengeStartRequest {
  email: string;
  challengeType: ChallengeType;
}

export interface ChallengeStartResponse {
  challengeId: string;
  challengeType: ChallengeType;
  expiresAt: string;
}

export interface ChallengeVerifyRequest {
  challengeId: string;
  code: string;
}

export interface ChallengeVerifyResponse {
  user: ChallengeVerifyUser;
  session: ChallengeVerifySession;
}

export interface ChallengeVerifyUser {
  id: string;
}

export interface ChallengeVerifySession {
  id: string;
  accessToken: string;
  refreshToken: string;
}

export type ChallengeStartPath = '/api/v1/auth/challenge/start';
export type ChallengeVerifyPath = '/api/v1/auth/challenge/verify';
