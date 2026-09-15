import { authChallengeApi } from '@/modules/auth/api/main/challenge.api';
import { AuthFlow } from '@/modules/auth/components/AuthFlow';

export function AuthPage() {
  return <AuthFlow client={authChallengeApi} />;
}
