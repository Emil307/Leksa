interface BrandStageProps {
  tagline: string;
}

const WORD_CARD = 'absolute w-50 rounded-[1.125rem] border border-line bg-ink/70 px-4 py-3.5 backdrop-blur-sm';

const WORD_CARDS = [
  { term: 'outspoken', meaning: 'откровенный', placement: 'top-0 left-0 -rotate-5' },
  { term: 'fluent', meaning: 'беглый', placement: 'top-13 left-17.5 rotate-3' },
  { term: 'confident', meaning: 'уверенный', placement: 'top-27.5 left-32.5 -rotate-2' },
];

export function BrandStage({ tagline }: BrandStageProps) {
  return (
    <>
      <section className="relative z-1 min-h-75 flex-1 px-5.5 pt-7">
        <div data-testid="app-title" className="font-heading text-[1.375rem] font-extrabold tracking-[-0.02em]">
          Uwords
        </div>
        <div className="relative mt-6.5 h-47.5" aria-hidden="true">
          {WORD_CARDS.map((card) => (
            <div key={card.term} className={`${WORD_CARD} ${card.placement}`}>
              <b className="block font-heading text-lg font-bold">{card.term}</b>
              <span className="text-[0.8125rem] text-muted">{card.meaning}</span>
            </div>
          ))}
        </div>
      </section>
      <p className="relative z-1 my-3.5 px-5.5 pb-6.5 text-sm leading-[1.45] text-muted">{tagline}</p>
    </>
  );
}
