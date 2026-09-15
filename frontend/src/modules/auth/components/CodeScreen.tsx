import type { FormEvent } from 'react';
import type { CodeScreenProps, ConfirmButtonMode, ResendControlView } from '@/modules/auth/types';
import { PrimaryButton } from '@/shared/ui/PrimaryButton';
import { SecondaryLink } from '@/shared/ui/SecondaryLink';
import { FieldLabel, Lead, LeadStrong, Sheet, SheetTitle } from '@/shared/ui/Sheet';
import { BrandStage } from './BrandStage';
import { CodeCells } from './CodeCells';
import { CodeScreenMessage } from './ScreenMessage';

const CONFIRM_BUTTON_LABELS: Record<ConfirmButtonMode, string> = {
  confirm: 'Подтвердить',
  verifying: 'Проверяем…',
  retry: 'Попробовать ещё раз',
};

function resendLabel(resend: ResendControlView): string {
  return resend.cooldownSecondsLeft === null
    ? 'Отправить новый код'
    : `Новый код можно запросить через ${resend.cooldownSecondsLeft} с`;
}

export function CodeScreen({
  view,
  onCellInput,
  onCellBackspace,
  onConfirm,
  onResend,
  onChangeEmail,
}: CodeScreenProps) {
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (view.confirmEnabled) onConfirm();
  };

  return (
    <>
      <BrandStage tagline="Проверьте почту — письмо приходит за несколько секунд." />
      <Sheet testId="code-screen">
        <SheetTitle>Введите код из письма</SheetTitle>
        <Lead>
          Отправили на <LeadStrong testId="code-email">{view.email}</LeadStrong>.{' '}
          {view.expired ? (
            <>
              Код <LeadStrong>больше не действует</LeadStrong>.
            </>
          ) : (
            <>
              Код действует ещё <LeadStrong testId="code-countdown">{view.countdown}</LeadStrong>
            </>
          )}
        </Lead>
        <form onSubmit={submit} noValidate>
          <FieldLabel>Код из письма</FieldLabel>
          <CodeCells
            cells={view.cells}
            focusedCell={view.focusedCell}
            enabled={view.cellsEnabled}
            tone={view.cellsTone}
            onInput={onCellInput}
            onBackspace={onCellBackspace}
          />
          {view.message && <CodeScreenMessage message={view.message} />}
          <PrimaryButton
            testId="confirm-button"
            label={CONFIRM_BUTTON_LABELS[view.confirmButton]}
            disabled={!view.confirmEnabled}
            busy={view.confirmButton === 'verifying'}
            onClick={onConfirm}
          />
        </form>
        <div className="mt-5 flex flex-col items-start gap-3.5 text-[0.9375rem]">
          <SecondaryLink
            testId="resend-button"
            label={resendLabel(view.resend)}
            disabled={!view.resend.enabled}
            onClick={onResend}
          />
          <SecondaryLink
            testId="change-email-link"
            label="Изменить адрес"
            disabled={!view.changeEmailEnabled}
            onClick={onChangeEmail}
          />
        </div>
      </Sheet>
    </>
  );
}
