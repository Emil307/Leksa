# UI Conventions

## Visual language

- Uwords authentication uses a near-black violet canvas (`#0B0712`) with restrained violet (`#6C35F0`) and lime (`#DFFF4F`) light blooms.
- Telegram-owned actions use Telegram blue (`#229ED9`) and remain visually distinct from Uwords primary actions.
- Headings use Manrope at 700–800 weight; body and service text use Inter at 400–600.
- The recurring signature element is an offset stack of translucent word cards behind the authentication surface.
- Surfaces are opaque enough for accessible contrast; blur and gradients are ambient decoration, not containers for body copy.

## Layout

- Desktop authentication uses a split stage: brand narrative on the left and one focused action panel on the right.
- Mobile authentication uses a full-height atmospheric shell with the focused action in a bottom sheet.
- A screen presents one primary action. Secondary actions are text links or quiet outlined buttons.
- Telegram OIDC confirmation is visually provider-owned: white Telegram surface, Telegram blue action, explicit Uwords destination.

## Interaction states

- Pending states always name the external step and offer a safe way back.
- Success states avoid exposing session or token details and continue into the product automatically.
- Errors use one safe message, a retry action, and no provider diagnostics.
- Mini App bootstrap separates evidence checking, product loading, and recoverable failure into distinct states.

## Accessibility and implementation

- Body text has at least 4.5:1 contrast; focus rings use `#DFFF4F` on dark surfaces and `#229ED9` on light surfaces.
- Icons come from Lucide; no inline SVG paths.
- User name, avatar, handle, and status are dynamic values in implementation even when a mockup shows an example.
- Desktop and mobile mockups keep state parity and use the same action labels.


## Email-code entry (Story 07)

- The Mini App ships mobile-only: the bottom sheet from the auth layout is the whole screen, and on a wide viewport it is simply centered. No desktop split stage is drawn for it.
- One-time codes use six equal cells; the active cell carries the lime focus ring, a rejected code turns every cell's border to `#FF7A8A`, an expired code dims the cells and closes them.
- Countdowns are service-supplied values rendered as `m:ss` inside body copy (code expiry) or inside the quiet secondary link (resend cooldown). A running cooldown turns the link into muted text; nothing else on the screen changes.
- Secondary actions on the code screen stack vertically under the primary button: resend first, change address second, each with its Lucide icon.
- The signed-in placeholder shows a lime check tile, a heading, and one line of copy — no profile data, no session details.
