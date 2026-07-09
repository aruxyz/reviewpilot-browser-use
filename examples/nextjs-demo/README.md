# ReviewPilot Demo - Next.js App with Intentional UX Bugs

A minimal Next.js 14 (App Router) demo app containing **5 intentional UX bugs**
for [ReviewPilot](https://github.com/browser-use/reviewpilot) - an AI browser QA
tool - to detect in demos and screencasts.

> **Do NOT fix these bugs.** They are planted on purpose. Every bug is marked with
> a `BUG #N (intentional)` comment in the source.

## Run

```bash
npm install
npm run dev      # starts on http://localhost:3000
```

Or build & run the production bundle:

```bash
npm install
npm run build
npm run start    # starts on http://localhost:3000
```

Requires Node 18+ (developed and verified on Node 22).

## Pages

| Route     | Description                                  |
| --------- | -------------------------------------------- |
| `/`       | Homepage: hero + pricing CTA + footer        |
| `/login`  | Login form (broken)                          |
| `/pricing`| Pricing tiers with a "Get started" CTA       |

## The 5 Intentional Bugs

### Bug 1 - Mobile navbar overflow
- **File:** `components/Navbar.tsx`
- **Symptom:** On viewports <= 390px the navbar links overflow horizontally. There
  is no hamburger menu and no responsive collapse - the links use a single `flex`
  row with `whitespace-nowrap`, so they get cut off and/or cause horizontal page
  scroll.
- **How to detect:** Set viewport to 390x844 (or smaller). Observe horizontal
  scroll or clipped nav links.

### Bug 2 - Login button stays disabled
- **File:** `app/login/page.tsx`
- **Symptom:** The "Sign In" button is hardcoded `disabled={true}` and never
  becomes enabled, even when both the email and password fields are filled. The
  disabled state is not wired to form validation.
- **How to detect:** Open `/login`, type into both fields, and observe the button
  remains greyed out / non-clickable.

### Bug 3 - Pricing CTA hidden below fold on mobile
- **File:** `app/page.tsx`
- **Symptom:** The homepage hero section uses `py-96` (384px) vertical padding on
  mobile, pushing the "View Pricing Plans" CTA below the fold on viewports
  <= 390px. The CTA is present in the DOM but requires scrolling to reach. On
  desktop the padding shrinks to `py-16` so the CTA is visible.
- **How to detect:** Load `/` at 390x844 and take a screenshot of the initial
  viewport - the CTA is not visible. Scroll down to find it.

### Bug 4 - Broken footer link (404)
- **File:** `components/Footer.tsx`
- **Symptom:** The "Privacy Policy" and "Terms of Service" footer links point to
  `/nonexistent-page`, a route that does not exist. Clicking returns a 404.
- **How to detect:** Click either footer link and observe the Next.js 404 page.

### Bug 5 - Unclear form validation
- **File:** `app/login/page.tsx`
- **Symptom:** The login form shows a generic error banner ("Error 001: Invalid
  input") with no field-level indicators - no red border, no `aria-invalid`, no
  helper text under the inputs. The user cannot tell which field is wrong or what
  the problem is.
- **How to detect:** Open `/login`, type into either field, and observe the
  generic error with no per-field cues (inputs keep their neutral grey border).

## File Tree

```
nextjs-demo/
├── README.md
├── package.json
├── tsconfig.json
├── next.config.mjs
├── postcss.config.mjs
├── tailwind.config.ts
├── next-env.d.ts
├── .gitignore
├── app/
│   ├── globals.css
│   ├── layout.tsx
│   ├── page.tsx              # Bug 3
│   ├── login/
│   │   └── page.tsx          # Bugs 2 + 5
│   └── pricing/
│       └── page.tsx
└── components/
    ├── Navbar.tsx            # Bug 1
    └── Footer.tsx            # Bug 4
```

## Tech Stack

- Next.js 14 (App Router)
- React 18
- TypeScript 5
- Tailwind CSS 3

## Notes

- There is no backend, database, or real authentication. All pages are static.
- `/nonexistent-page` is intentionally not implemented so that the footer links
  produce a real 404 (Next.js default 404 page).
- The app is deliberately plain-looking. It is a bug-demo app, not a portfolio
  piece.
