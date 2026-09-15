# Tailwind CSS Conventions

Tech binding for `frontend-rules.md` CSS concerns. Shared section structure: `.claude/templates/coding/coding-sections.md`.

## Utility Framework

- CSS utility framework: Tailwind CSS v4. Theme stylesheet: `frontend/src/app/theme.css`.
- `theme.css` contains only: `@import 'tailwindcss'`, font `@import`s, the `@theme` token block (`--color-*`, `--font-*`, `--radius-*`, `--shadow-*`), `:root` variables that are not tokens, `@layer base` (body, resets), and `@keyframes`. No `@layer components`, no `@apply` outside `@layer base`, no selector that names a component.
- Component styles are Tailwind utilities in the component's `className`. A chain of any length stays in the component: `className="flex h-13 items-center gap-2.5 rounded-2xl border border-line bg-field px-4 text-base focus-within:border-lime-bloom"`.
- Raw values are theme tokens, never arbitrary values. `bg-[#211829]` is a leak: add `--color-field: #211829` to `@theme` and write `bg-field`. Same for fonts (`font-heading`), non-scale radii (`rounded-sheet`), and shadows. Arbitrary values are allowed only for one-off geometry a token would not name (`top-[-7.5rem]`, `blur-[4.375rem]`, `rotate-[-5deg]`).
- Arbitrary lengths are `rem`, never `px`: `text-[0.9375rem]`, `w-[9.375rem]` -- not `text-[15px]`, `w-[150px]`. Convert at `1rem = 16px`. Only `border`/`outline` hairlines and `@media` breakpoints stay in `px`. Scale utilities (`p-4`, `text-sm`) already resolve to `rem`.
- Repeated utility sets across components: extract a shared component in `frontend/src/shared/ui/`, never a CSS class. Repeated within one component: a `const` string above the component. Conditional classes: a helper function above the component (see `frontend-rules.md`, "Conditional Class Logic").
- Built-in animations (`animate-spin`, `animate-pulse`) replace hand-written `@keyframes` where they match.

## Icons

- Icon library: `lucide-react` (v0.487.0, already in `package.json`).
- Import syntax: `import { HelpCircle } from 'lucide-react'`.
- NEVER write inline SVG `<path d="...">` or `<svg>` elements.
- Standard sizes: `size={16}` inline text, `size={20}` nav items, `size={24}` prominent.
