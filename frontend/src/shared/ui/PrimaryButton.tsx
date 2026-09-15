import type { PrimaryButtonProps } from '@/modules/auth/types';

const BUTTON =
  'mt-5 flex h-13.5 w-full cursor-pointer items-center justify-center gap-2.5 rounded-[1.125rem] bg-lime-bloom text-base font-semibold text-canvas disabled:cursor-default';

const DISABLED_LOOK = {
  idle: 'disabled:bg-lime-bloom/28 disabled:text-canvas/70',
  busy: 'disabled:bg-lime-bloom/55 disabled:text-canvas',
};

export function PrimaryButton({ testId, label, disabled, busy, onClick }: PrimaryButtonProps) {
  return (
    <button
      type="button"
      data-testid={testId}
      className={`${BUTTON} ${busy ? DISABLED_LOOK.busy : DISABLED_LOOK.idle}`}
      disabled={disabled}
      onClick={onClick}
    >
      {busy && (
        <span
          className="h-5 w-5 animate-spin rounded-full border-[0.15625rem] border-canvas/25 border-t-canvas"
          aria-hidden="true"
        />
      )}
      {label}
    </button>
  );
}
