import { CircleAlert, Clock } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { ReactNode } from 'react';
import { LeadStrong } from '@/shared/ui/Sheet';
import type {
  AuthTestId,
  CodeScreenMessageKind,
  CodeScreenMessageProps,
  EmailScreenMessageKind,
  EmailScreenMessageProps,
  ScreenMessageTone,
} from '@/modules/auth/types';

const ICON_SIZE = 18;

const TONE_ICONS: Record<ScreenMessageTone, LucideIcon> = { error: CircleAlert, muted: Clock };
const TONE_COLORS: Record<ScreenMessageTone, string> = { error: 'text-danger', muted: 'text-muted' };

interface MessageText {
  tone: ScreenMessageTone;
  render: (secondsLeft: number | null) => ReactNode;
}

interface ScreenMessageProps {
  testId: AuthTestId;
  text: MessageText;
  secondsLeft: number | null;
}

function ScreenMessage({ testId, text, secondsLeft }: ScreenMessageProps) {
  const Icon = TONE_ICONS[text.tone];
  return (
    <div
      data-testid={testId}
      className={`mt-3 flex items-start gap-2.5 text-sm leading-[1.4] ${TONE_COLORS[text.tone]}`}
      role="status"
    >
      <Icon size={ICON_SIZE} className="mt-[0.0625rem] flex-none" aria-hidden="true" />
      <span>{text.render(secondsLeft)}</span>
    </div>
  );
}

function RequestAgainIn({ secondsLeft }: { secondsLeft: number | null }) {
  return (
    <>
      Новый код можно запросить через <LeadStrong>{secondsLeft} с</LeadStrong>.
    </>
  );
}

const UNAVAILABLE: MessageText = { tone: 'error', render: () => 'Сервис временно недоступен, попробуйте позже.' };

const EMAIL_MESSAGES: Record<EmailScreenMessageKind, MessageText> = {
  'invalid-email': { tone: 'error', render: () => 'Проверьте адрес — на такой мы не сможем отправить письмо.' },
  unavailable: UNAVAILABLE,
  'email-cooldown': {
    tone: 'muted',
    render: (secondsLeft) => (
      <>
        Код на этот адрес уже отправлен. <RequestAgainIn secondsLeft={secondsLeft} />
      </>
    ),
  },
};

const CODE_MESSAGES: Record<CodeScreenMessageKind, MessageText> = {
  'code-rejected': { tone: 'error', render: () => 'Код не подошёл. Проверьте письмо или запросите новый.' },
  'code-expired': { tone: 'muted', render: () => 'Время кода вышло. Запросите новый — он придёт на тот же адрес.' },
  unavailable: UNAVAILABLE,
  'resend-cooldown': { tone: 'muted', render: (secondsLeft) => <RequestAgainIn secondsLeft={secondsLeft} /> },
};

export function EmailScreenMessage({ message }: EmailScreenMessageProps) {
  return <ScreenMessage testId="email-message" text={EMAIL_MESSAGES[message.kind]} secondsLeft={message.secondsLeft} />;
}

export function CodeScreenMessage({ message }: CodeScreenMessageProps) {
  return <ScreenMessage testId="code-message" text={CODE_MESSAGES[message.kind]} secondsLeft={message.secondsLeft} />;
}
