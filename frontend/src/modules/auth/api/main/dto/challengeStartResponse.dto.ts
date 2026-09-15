import { isJsonObject, isString } from '@/shared/utils';
import type { ChallengeStartResponse, ChallengeType } from '../../../types';

export class ChallengeStartResponseDto {
  private constructor(
    readonly challengeId: string,
    readonly challengeType: ChallengeType,
    readonly expiresAt: string
  ) {}

  static parse(body: unknown): ChallengeStartResponseDto | null {
    if (!isJsonObject(body)) return null;
    const { challengeId, challengeType, expiresAt } = body;
    if (!isString(challengeId) || challengeType !== 'EMAIL_CODE' || !isString(expiresAt)) return null;
    return new ChallengeStartResponseDto(challengeId, challengeType, expiresAt);
  }

  toChallenge(): ChallengeStartResponse {
    return { challengeId: this.challengeId, challengeType: this.challengeType, expiresAt: this.expiresAt };
  }
}
