import { Pencil, RefreshCw } from 'lucide-react';
import type { ReactNode } from 'react';
import type { AuthTestId, SecondaryLinkProps } from '@/modules/auth/types';

const ICON_SIZE = 16;

const ICONS: Partial<Record<AuthTestId, ReactNode>> = {
  'resend-button': <RefreshCw size={ICON_SIZE} aria-hidden="true" />,
  'change-email-link': <Pencil size={ICON_SIZE} aria-hidden="true" />,
};

export function SecondaryLink({ testId, label, disabled, onClick }: SecondaryLinkProps) {
  return (
    <button
      type="button"
      data-testid={testId}
      className="inline-flex cursor-pointer items-center gap-1.5 bg-transparent p-0 font-semibold text-ink-text disabled:cursor-default disabled:font-medium disabled:text-muted"
      disabled={disabled}
      onClick={onClick}
    >
      {ICONS[testId]}
      {label}
    </button>
  );
}
