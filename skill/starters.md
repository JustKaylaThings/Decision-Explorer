# Starter questions for each stage

A curated set of common decisions for each SDLC phase, so a builder can see *what's worth
deciding* at each stage and decide the ones that apply. This is the `starters` subcommand
(d58). It stays **capture-only**: the questions are prompts — nothing is written until the
user answers one and confirms, through the normal `add` flow.

## Contents
- When to run
- Workflow (read coverage → offer → capture)
- The question set (six phases)

## When to run
- The user names it: `/decision-tree starters` (or `/decide starters`), optionally with a phase
  (`/decide starters Design`).
- Proactively, lightly: when a user is clearly working in a stage that has **no decisions yet**,
  you may mention that this stage has starter questions — then stop. Don't nag.

## Workflow

```
Starters progress:
- [ ] 1. Read what's already covered
- [ ] 2. Hide covered starters
- [ ] 3. Offer the rest for this phase
- [ ] 4. Capture only what the user decides (confirm-at-the-moment)
```

**1. Read what's already covered**
Read the project's decisions (`decisions/NNNN-*.json`). For each phase, note which topics already
have a decision. If a phase argument was given, scope to that phase; otherwise walk all six in
lifecycle order.

**2. Hide covered starters (coverage-aware — d58)**
Drop any starter whose topic is **already covered** by an existing decision in that phase — judge by
meaning, not exact wording (a decision titled "Where notes are saved" covers "Where data is
stored"). If every starter in a phase is covered, say so in one line and move on; don't pad.

**3. Offer the rest for this phase**
List the remaining starters as plain options the user can pick. Present them, then stop — this is an
invitation, not a form. The user chooses which (if any) to decide now; skipping is fine.

**4. Capture only what the user decides**
For each starter the user decides, run the normal **`add`** flow (confirm-at-the-moment): draft the
title, options, tradeoffs, the choice and why; the user confirms or edits; then write a **decided**
decision in that phase and regenerate. Reuse the starter's plain title as the decision title unless
the user rewrites it. Write nothing for starters the user skips.

## The question set (six phases)

Each entry is a plain everyday-topic title and the question it answers. These are prompts to adapt,
not a script — reword to fit the project.

**Requirements**
- *Who the app is for* — who is the primary user and the one job they need done?
- *The one thing it must do* — what must the first version nail?
- *What's out of scope for now* — what are we deliberately not building yet?
- *How we'll know it's working* — what signal says it's succeeding?

**Design**
- *Where data is stored* — on the device, in the cloud, or both?
- *How people sign in* — accounts, guest, or no login?
- *Works offline or online-only* — does it need to run without a connection?
- *How it looks and feels* — what's the visual style?

**Implementation**
- *What it's built with* — which language or framework?
- *What we use vs build ourselves* — auth, payments, email: buy or build?
- *How errors are handled* — what happens when something fails?
- *Where the code lives* — repo, branching, backups?

**Testing**
- *How we check it works* — manual, automated, or both?
- *What must never break* — which flows are critical enough to always test?
- *Who tries it before launch* — internal, beta users, or open?

**Deployment**
- *Where it's hosted* — which platform runs it?
- *How updates reach users* — what's the release process?
- *What launch looks like* — soft launch, waitlist, or public?

**Maintenance**
- *How we hear about problems* — error alerts and user reports?
- *What we watch after launch* — which metrics or logs?
- *When we revisit decisions* — how do we decide to change course?
