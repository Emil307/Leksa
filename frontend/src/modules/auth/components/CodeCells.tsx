import { useEffect, useRef } from 'react';
import type { KeyboardEvent } from 'react';
import type { CodeCellIndex, CodeCellTestId, CodeCellsProps, CodeCellsTone } from '@/modules/auth/types';

const CELL_INDEXES: readonly CodeCellIndex[] = [0, 1, 2, 3, 4, 5];

const CELL =
  'h-14 w-0 min-w-0 flex-1 rounded-[0.875rem] border bg-field p-0 text-center font-heading text-[1.375rem] font-bold text-ink-text outline-none focus:border-lime-bloom';

const CELL_TONES: Record<CodeCellsTone, string> = {
  normal: 'border-line',
  error: 'border-danger',
  disabled: 'border-line opacity-45',
};

function cellTestId(index: CodeCellIndex): CodeCellTestId {
  return `code-cell-${index}`;
}

export function CodeCells({ cells, focusedCell, enabled, tone, onInput, onBackspace }: CodeCellsProps) {
  const inputs = useRef<Array<HTMLInputElement | null>>([]);

  useEffect(() => {
    if (enabled) inputs.current[focusedCell]?.focus();
  }, [focusedCell, enabled]);

  const keyDown = (index: CodeCellIndex) => (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Backspace' && cells[index] === '') {
      event.preventDefault();
      onBackspace(index);
    }
  };

  return (
    <div className="flex gap-2">
      {CELL_INDEXES.map((index) => (
        <input
          key={index}
          ref={(element) => {
            inputs.current[index] = element;
          }}
          data-testid={cellTestId(index)}
          className={`${CELL} ${CELL_TONES[tone]}`}
          type="text"
          inputMode="numeric"
          autoComplete="one-time-code"
          aria-label={`Цифра ${index + 1}`}
          value={cells[index]}
          disabled={!enabled}
          onChange={(event) => onInput(index, event.target.value)}
          onKeyDown={keyDown(index)}
        />
      ))}
    </div>
  );
}
