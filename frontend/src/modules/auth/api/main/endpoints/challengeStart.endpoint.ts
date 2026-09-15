import type { ApiEndpoint } from '@/shared/api';
import type { ChallengeStartPath, ChallengeStarted } from '../../../types';
import { ChallengeStartResponseDto } from '../dto/challengeStartResponse.dto';

const START_PATH: ChallengeStartPath = '/api/v1/auth/challenge/start';

export const challengeStartEndpoint: ApiEndpoint<ChallengeStarted> = {
  path: START_PATH,
  parse: (body) => {
    const started = ChallengeStartResponseDto.parse(body);
    return started ? { kind: 'started', challenge: started.toChallenge() } : null;
  },
};
