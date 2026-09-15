import type { ComputeSecondsLeft, FormatCountdown, ParseExpiresAt } from '../../types';

const MS_PER_SECOND = 1000;
const SECONDS_PER_MINUTE = 60;

export const parseExpiresAt: ParseExpiresAt = (expiresAt) => Date.parse(expiresAt);

export const computeSecondsLeft: ComputeSecondsLeft = (expiresAtEpochMs, nowEpochMs) =>
  Math.max(0, Math.ceil((expiresAtEpochMs - nowEpochMs) / MS_PER_SECOND));

export const formatCountdown: FormatCountdown = (seconds) => {
  const minutes = Math.floor(seconds / SECONDS_PER_MINUTE);
  const rest = seconds % SECONDS_PER_MINUTE;
  return `${minutes}:${String(rest).padStart(2, '0')}`;
};
