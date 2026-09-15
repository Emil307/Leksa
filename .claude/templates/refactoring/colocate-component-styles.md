# Colocate Component Styles

**When to use:** The theme stylesheet contains a selector that names a component (`.auth-card`, `.btn-primary`, `.field:focus-within`), a `@layer components` block, or an `@apply` outside `@layer base` — or a component uses an arbitrary raw value (`bg-[#211829]`, `font-['Manrope']`) that the theme has no token for.

**Rule:** the theme stylesheet holds only tokens, variables, the base layer, font imports and keyframes. Everything a single component looks like lives on that component's markup as utilities.

## Step 1: Inventory the stylesheet

List every selector outside `@theme`, `:root`, `@layer base`, `@keyframes`, `@font-face`. For each, find the consuming component (`Grep pattern="className=.*\bselector-name\b"`).

## Step 2: Promote raw values to tokens

Any hex color, font family, non-scale radius or shadow that the selector uses and `@theme` does not name becomes a token first:

```css
@theme {
  --color-field: #211829;
  --color-line: rgba(255, 255, 255, 0.09);
  --font-heading: 'Manrope', system-ui, sans-serif;
}
```

## Step 3: Translate declarations into utilities

Map each declaration to a utility. Scale values use the scale (`padding: 1rem` → `p-4`); off-scale values use an arbitrary `rem` value (`height: 3.25rem` → `h-[3.25rem]`); pseudo-classes become variants (`:focus-within` → `focus-within:`); descendant state selectors (`.cells-error .cell`) become a class computed by a helper on the child.

```css
/* Before — theme.css */
.field {
  display: flex; align-items: center; gap: 0.625rem; height: 3.25rem;
  padding: 0 1rem; border-radius: 1rem; background: var(--color-field);
  border: 1px solid var(--color-line); font-size: 1rem;
}
.field:focus-within { border-color: var(--color-lime-bloom); }
.field-error { border-color: var(--color-danger); }
```

```tsx
// After — EmailScreen.tsx
const FIELD = 'flex h-[3.25rem] items-center gap-2.5 rounded-2xl border border-line bg-field px-4 text-base focus-within:border-lime-bloom';

function fieldClassName(tone: FieldTone): string {
  return tone === 'error' ? `${FIELD} border-danger` : FIELD;
}
```

## Step 4: Delete the selector

Remove the selector from the stylesheet. When the last one goes, remove the `@layer components` block itself.

## Step 5: Repetition

If the same utility set now appears in 2+ components, extract a shared component (`extract-shared-ui.md`), not a class. If it appears 2+ times within one component, hoist a `const`.

## Verification

1. `cd frontend && npx vitest run` — all tests pass
2. `cd frontend && npx vite build` — builds
3. `grep -n "@layer components\|@apply" frontend/src/app/theme.css` — only `@apply` inside `@layer base` remains
4. Visual check against the mockup — appearance unchanged
