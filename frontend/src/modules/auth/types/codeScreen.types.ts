export type CodeCellIndex = 0 | 1 | 2 | 3 | 4 | 5;

export type CodeCells = readonly [string, string, string, string, string, string];

export interface CodeCellsTransition {
  cells: CodeCells;
  focusedCell: CodeCellIndex;
}

export type CodeScreenStatus = 'waiting' | 'submitting' | 'rejected' | 'expired' | 'unavailable';

export interface CodeScreenState {
  email: string;
  challengeId: string;
  expiresAtEpochMs: number;
  secondsLeft: number;
  cells: CodeCells;
  focusedCell: CodeCellIndex;
  status: CodeScreenStatus;
  resendCooldownSecondsLeft: number | null;
  pendingRequestId: number | null;
}

export type CodeScreenMessageKind = 'code-rejected' | 'code-expired' | 'unavailable' | 'resend-cooldown';

export interface CodeScreenMessage {
  kind: CodeScreenMessageKind;
  secondsLeft: number | null;
}

export type ConfirmButtonMode = 'confirm' | 'verifying' | 'retry';

export type CodeCellsTone = 'normal' | 'error' | 'disabled';

export interface ResendControlView {
  enabled: boolean;
  cooldownSecondsLeft: number | null;
}

export interface CodeScreenView {
  email: string;
  countdown: string;
  expired: boolean;
  cells: CodeCells;
  focusedCell: CodeCellIndex;
  cellsEnabled: boolean;
  cellsTone: CodeCellsTone;
  confirmEnabled: boolean;
  confirmButton: ConfirmButtonMode;
  resend: ResendControlView;
  changeEmailEnabled: boolean;
  message: CodeScreenMessage | null;
}
