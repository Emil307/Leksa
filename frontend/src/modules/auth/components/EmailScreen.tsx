import { Mail } from 'lucide-react';
import type { FormEvent } from 'react';
import type { EmailScreenProps, EmailScreenView, RequestCodeButtonMode } from '@/modules/auth/types';
import { PrimaryButton } from '@/shared/ui/PrimaryButton';
import { FieldLabel, Lead, Sheet, SheetTitle } from '@/shared/ui/Sheet';
import { BrandStage } from './BrandStage';
import { EmailScreenMessage } from './ScreenMessage';

const ICON_SIZE = 20;

const REQUEST_BUTTON_LABELS: Record<RequestCodeButtonMode, string> = {
  request: 'Получить код',
  sending: 'Отправляем код…',
  retry: 'Попробовать ещё раз',
};

const FIELD =
  'flex h-13 items-center gap-2.5 rounded-2xl border bg-field px-4 text-base focus-within:border-lime-bloom focus-within:ring-[0.1875rem] focus-within:ring-lime-bloom/18';

const FIELD_TONES: Record<EmailScreenView['fieldTone'], string> = {
  normal: 'border-line',
  error: 'border-danger',
  disabled: 'border-line opacity-45',
};

export function EmailScreen({ view, onEmailChange, onRequestCode }: EmailScreenProps) {
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (view.requestEnabled) onRequestCode();
  };

  return (
    <>
      <BrandStage tagline="Одна почта — один аккаунт на сайте, в Telegram и в боте." />
      <Sheet testId="email-screen">
        <SheetTitle testId="email-title">Войти или создать аккаунт</SheetTitle>
        <Lead>Пришлём код на почту — пароль не нужен.</Lead>
        <form onSubmit={submit} noValidate>
          <FieldLabel htmlFor="email">Почта</FieldLabel>
          <div className={`${FIELD} ${FIELD_TONES[view.fieldTone]}`}>
            <Mail size={ICON_SIZE} className="flex-none text-muted" aria-hidden="true" />
            <input
              data-testid="email-input"
              id="email"
              className="min-w-0 flex-1 bg-transparent text-ink-text caret-lime-bloom outline-none placeholder:text-placeholder"
              type="email"
              inputMode="email"
              autoComplete="email"
              autoFocus
              placeholder="you@example.com"
              value={view.email}
              disabled={!view.inputEnabled}
              onChange={(event) => onEmailChange(event.target.value)}
            />
          </div>
          {view.message && <EmailScreenMessage message={view.message} />}
          <PrimaryButton
            testId="request-code-button"
            label={REQUEST_BUTTON_LABELS[view.requestButton]}
            disabled={!view.requestEnabled}
            busy={view.requestButton === 'sending'}
            onClick={onRequestCode}
          />
        </form>
        <p className="mt-4.5 mb-3.25 text-center text-[0.8125rem] leading-[1.45] text-muted">
          Продолжая, вы соглашаетесь с условиями Uwords.
        </p>
      </Sheet>
    </>
  );
}
