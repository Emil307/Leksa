import type { ReactNode } from 'react';

interface SheetProps {
  testId: string;
  children: ReactNode;
}

interface SheetTextProps {
  testId?: string;
  children: ReactNode;
}

export function Sheet({ testId, children }: SheetProps) {
  return (
    <section
      data-testid={testId}
      className="relative z-2 -mt-2 rounded-t-4xl border-t border-line bg-ink/97 px-5.5 pt-7.5 pb-8.5"
    >
      <div className="mx-auto -mt-3 mb-5.5 h-1 w-10 rounded-xs bg-white/18" aria-hidden="true" />
      {children}
    </section>
  );
}

export function SheetTitle({ testId, children }: SheetTextProps) {
  return (
    <h1 data-testid={testId} className="mb-1.5 font-heading text-2xl leading-[1.15] font-extrabold tracking-[-0.02em]">
      {children}
    </h1>
  );
}

export function Lead({ children }: SheetTextProps) {
  return <p className="mb-5.5 text-[0.9375rem] leading-[1.45] text-muted">{children}</p>;
}

export function LeadStrong({ testId, children }: SheetTextProps) {
  return (
    <strong data-testid={testId} className="font-semibold text-ink-text">
      {children}
    </strong>
  );
}

export function FieldLabel({ htmlFor, children }: { htmlFor?: string; children: ReactNode }) {
  return (
    <label htmlFor={htmlFor} className="mb-2 block text-[0.8125rem] font-semibold text-muted">
      {children}
    </label>
  );
}
