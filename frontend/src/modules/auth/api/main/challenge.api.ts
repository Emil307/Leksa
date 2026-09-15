import { apiClient, type ApiClient } from '@/shared/api';
import type {
  ChallengeApiClient,
  ChallengeStartOutcome,
  ChallengeStartRequest,
  ChallengeVerifyOutcome,
  ChallengeVerifyRequest,
} from '../../types';
import { challengeStartEndpoint } from './endpoints/challengeStart.endpoint';
import { challengeVerifyEndpoint } from './endpoints/challengeVerify.endpoint';

export class AuthChallengeApi implements ChallengeApiClient {
  constructor(private readonly api: ApiClient) {}

  startChallenge = (request: ChallengeStartRequest): Promise<ChallengeStartOutcome> =>
    this.api.call(challengeStartEndpoint, request);

  verifyChallenge = (request: ChallengeVerifyRequest): Promise<ChallengeVerifyOutcome> =>
    this.api.call(challengeVerifyEndpoint, request);
}

export const authChallengeApi = new AuthChallengeApi(apiClient);
