import { isJsonObject, isString } from '@/shared/utils';
import type { AuthSession, ChallengeVerifySession, ChallengeVerifyUser } from '../../../types';

export class ChallengeVerifyResponseDto {
  private constructor(
    readonly user: ChallengeVerifyUser,
    readonly session: ChallengeVerifySession
  ) {}

  static parse(body: unknown): ChallengeVerifyResponseDto | null {
    if (!isJsonObject(body) || !isJsonObject(body.user) || !isJsonObject(body.session)) return null;
    const { id: userId } = body.user;
    const { id: sessionId, accessToken, refreshToken } = body.session;
    if (!isString(userId) || !isString(sessionId) || !isString(accessToken) || !isString(refreshToken)) return null;
    return new ChallengeVerifyResponseDto({ id: userId }, { id: sessionId, accessToken, refreshToken });
  }

  toSession(): AuthSession {
    return {
      userId: this.user.id,
      sessionId: this.session.id,
      accessToken: this.session.accessToken,
      refreshToken: this.session.refreshToken,
    };
  }
}
