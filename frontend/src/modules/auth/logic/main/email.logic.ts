import type {
  BuildChallengeStartRequest,
  EmailMaxOctets,
  EmailScreenMessage,
  EmailScreenState,
  EmailScreenView,
  SelectEmailScreenView,
  ValidateEmail,
} from '../../types';
import { countUtf8Octets } from '@/shared/utils';

const EMAIL_MAX_OCTETS: EmailMaxOctets = 254;
const EMAIL_SHAPE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export const validateEmail: ValidateEmail = (email) => {
  if (email === '') return 'empty';
  if (!EMAIL_SHAPE.test(email)) return 'malformed';
  if (countUtf8Octets(email) > EMAIL_MAX_OCTETS) return 'too-long';
  return 'valid';
};

export const buildChallengeStartRequest: BuildChallengeStartRequest = (email) => ({
  email,
  challengeType: 'EMAIL_CODE',
});

const selectMessage = (state: EmailScreenState): EmailScreenMessage | null => {
  switch (state.status) {
    case 'invalid':
      return { kind: 'invalid-email', secondsLeft: null };
    case 'unavailable':
      return { kind: 'unavailable', secondsLeft: null };
    case 'cooldown':
      return { kind: 'email-cooldown', secondsLeft: state.cooldownSecondsLeft };
    default:
      return null;
  }
};

const lockedView = (state: EmailScreenState): EmailScreenView => ({
  email: state.email,
  inputEnabled: false,
  requestEnabled: false,
  requestButton: 'sending',
  fieldTone: 'disabled',
  message: null,
});

export const selectEmailScreenView: SelectEmailScreenView = (state) => {
  if (state.status === 'sending') return lockedView(state);
  const valid = validateEmail(state.email) === 'valid';
  return {
    email: state.email,
    inputEnabled: true,
    requestEnabled: valid && state.status !== 'cooldown',
    requestButton: state.status === 'unavailable' ? 'retry' : 'request',
    fieldTone: state.status === 'invalid' ? 'error' : 'normal',
    message: selectMessage(state),
  };
};
