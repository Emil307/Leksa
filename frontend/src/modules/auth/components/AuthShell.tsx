import type { AuthShellProps } from '@/modules/auth/types';

const BLOOM = 'pointer-events-none absolute rounded-full blur-[4.375rem]';

export function AuthShell({ children }: AuthShellProps) {
  return (
    <div className="relative mx-auto flex min-h-dvh w-full max-w-107.5 flex-col overflow-hidden bg-canvas">
      <div className={`${BLOOM} -top-30 -left-22.5 h-80 w-80 bg-violet-bloom opacity-55`} aria-hidden="true" />
      <div className={`${BLOOM} top-10 -right-27.5 h-55 w-55 bg-lime-bloom opacity-28`} aria-hidden="true" />
      {children}
    </div>
  );
}
