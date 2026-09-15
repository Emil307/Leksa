import type { ApiEndpoint } from '@/shared/api';
import type { ChallengeSignedIn, ChallengeVerifyPath } from '../../../types';
import { ChallengeVerifyResponseDto } from '../dto/challengeVerifyResponse.dto';

const VERIFY_PATH: ChallengeVerifyPath = '/api/v1/auth/challenge/verify';

export const challengeVerifyEndpoint: ApiEndpoint<ChallengeSignedIn> = {
  path: VERIFY_PATH,
  parse: (body) => {
    const verified = ChallengeVerifyResponseDto.parse(body);
    return verified ? { kind: 'signed-in', session: verified.toSession() } : null;
  },
};
