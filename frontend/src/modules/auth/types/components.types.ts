import type { ReactNode } from 'react';
import type { ChallengeApiClient } from './challengeClient.types';
import type { CodeCellIndex, CodeCells, CodeCellsTone, CodeScreenMessage, CodeScreenView } from './codeScreen.types';
import type { EmailScreenMessage, EmailScreenView } from './emailScreen.types';

export type AuthTestId =
  | 'email-screen'
  | 'email-title'
  | 'email-input'
  | 'email-message'
  | 'request-code-button'
  | 'code-screen'
  | 'code-email'
  | 'code-countdown'
  | 'code-cell-0'
  | 'code-cell-1'
  | 'code-cell-2'
  | 'code-cell-3'
  | 'code-cell-4'
  | 'code-cell-5'
  | 'code-message'
  | 'confirm-button'
  | 'resend-button'
  | 'change-email-link'
  | 'signed-in-screen'
  | 'signed-in-title';

export type CodeCellTestId = `code-cell-${CodeCellIndex}`;

export interface AuthFlowProps {
  client: ChallengeApiClient;
  now?: () => number;
}

export interface EmailScreenProps {
  view: EmailScreenView;
  onEmailChange: (email: string) => void;
  onRequestCode: () => void;
}

export interface CodeScreenProps {
  view: CodeScreenView;
  onCellInput: (index: CodeCellIndex, value: string) => void;
  onCellBackspace: (index: CodeCellIndex) => void;
  onConfirm: () => void;
  onResend: () => void;
  onChangeEmail: () => void;
}

export interface CodeCellsProps {
  cells: CodeCells;
  focusedCell: CodeCellIndex;
  enabled: boolean;
  tone: CodeCellsTone;
  onInput: (index: CodeCellIndex, value: string) => void;
  onBackspace: (index: CodeCellIndex) => void;
}

export type ScreenMessageTone = 'error' | 'muted';

export interface EmailScreenMessageProps {
  message: EmailScreenMessage;
}

export interface CodeScreenMessageProps {
  message: CodeScreenMessage;
}

export interface PrimaryButtonProps {
  testId: AuthTestId;
  label: string;
  disabled: boolean;
  busy: boolean;
  onClick: () => void;
}

export interface SecondaryLinkProps {
  testId: AuthTestId;
  label: string;
  disabled: boolean;
  onClick: () => void;
}

export type SignedInScreenProps = Record<never, never>;

export interface AuthShellProps {
  children: ReactNode;
}
