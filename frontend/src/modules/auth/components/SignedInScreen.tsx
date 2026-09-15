import { Check } from 'lucide-react';
import type { FC } from 'react';
import type { SignedInScreenProps } from '@/modules/auth/types';
import { Lead, SheetTitle } from '@/shared/ui/Sheet';

const CHECK_SIZE = 34;

export const SignedInScreen: FC<SignedInScreenProps> = () => {
  return (
    <section
      data-testid="signed-in-screen"
      className="relative z-1 flex flex-1 flex-col items-center justify-center px-7 text-center"
    >
      <div className="mb-5.5 grid h-18 w-18 place-items-center rounded-3xl border border-lime-bloom/40 bg-lime-bloom/14 text-lime-bloom">
        <Check size={CHECK_SIZE} aria-hidden="true" />
      </div>
      <SheetTitle testId="signed-in-title">Вы вошли</SheetTitle>
      <Lead>Ваш словарь скоро появится здесь.</Lead>
    </section>
  );
};
