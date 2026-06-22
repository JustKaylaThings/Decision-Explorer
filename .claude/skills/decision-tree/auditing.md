# Auditing an existing codebase to back-fill decisions

Use this to reconstruct a decision log for an app that was **built without one** (decision d34).
The decisions were already made — they were just never recorded. This flow **discovers, then
confirms**: it mines the code and git history to draft the load-bearing decisions, then interviews
the user to fill the *why* before anything is written. It is the normal confirm-at-the-moment model
run in reverse — the scan proposes, the user disposes. **Nothing is written without sign-off.**

## Contents
- When to run
- Scope: load-bearing only
- Workflow (discover → filter → draft → interview → confirm)
- Detection recipes
- Drafting rules
- Interview rules

## When to run
- The user names it: `/decision-tree audit <path>`, "audit this codebase", "back-fill decisions".
- `<path>` defaults to the project root. If the target has no `decisions/`, create the folder and
  `_project.json` (`{ "project": "<dir name>" }`) first, exactly as `add` would.
- If a decision log already exists, audit only **gap-fills** — skip topics already logged; never
  duplicate an existing decision (match by topic, not wording).

## Scope: load-bearing only
Capture the choices that would be expensive or risky to change — **not** every detectable pick.

- **Keep:** language & strictness, primary framework, data store, auth/identity, API style
  (REST/GraphQL/RPC), state management, styling approach, build/bundler tooling, hosting/deployment
  target, CI strategy, testing strategy, repo structure (monorepo vs single), and any key
  third-party integration the app is built around (payments, maps, analytics SDK).
- **Drop:** formatting prefs (Prettier/ESLint rules), minor utility libraries, lockfile churn,
  one-off helper choices, anything with no realistic alternative.
- **No silent caps:** when you drop candidates, `log`/tell the user the count and a one-line reason
  ("skipped 14 minor library picks — not load-bearing"), so "audited" never reads as "covered
  everything" when it didn't.

## Workflow

Copy this checklist and work through it:

```
Audit progress:
- [ ] 1. Discover (static scan + git history) — write nothing
- [ ] 2. Filter to load-bearing — report what was dropped
- [ ] 3. Draft candidate decisions
- [ ] 4. Interview to fill the "why" and confirm
- [ ] 5. Write approved decisions + regenerate (once, at the end)
```

**1. Discover — write nothing.** Run the detection recipes below over `<path>`. For each signal,
record a *candidate*: topic, the **what** (chosen), inferred **alternatives**, the **evidence**
(file path or commit), and the **gap** (what the code can't tell you — almost always the *why* and
the rejected options). Two evidence streams:
   - **Static structure** — manifests, config, directory layout (the recipes below).
   - **Git history** — `git log`, reverts, large rewrites, "switch from X to Y" / "migrate" /
     "replace" commit messages, and dependency add/remove over time. Each reversal is a candidate
     decision *with a built-in `history` entry* (the old choice → the new one, dated by the commit).

**2. Filter to load-bearing.** Apply the Scope rules. Tell the user what you kept and what you
dropped (with counts) before drafting.

**3. Draft.** For each kept candidate, draft a decision in the schema (see SKILL.md):
   - **title** plain and everyday (the recipes suggest titles); **question** it answers;
     **phase** (stack choices are usually `Design`; wiring/tooling `Implementation`);
     **category** (reuse existing strings); **options** = the chosen one **plus the plausible
     alternatives** for that slot (e.g. chosen Postgres → also MySQL, SQLite); **tradeoffs** per
     option using **verbatim-reused criteria**.
   - **rationale** starts as a clearly-marked placeholder (`«why — confirm»`) — never invent a
     reason. It's filled in stage 4.
   - **date** — back-log from the introducing commit's date when known
     (`git log --diff-filter=A --format=%cI -1 -- <file>`), time included; omit time if unknown.
   - **dependsOn** — wire the obvious chains (framework → language; deployment → framework;
     auth → data store).

**4. Interview — fill the why, confirm the drafts.** This is where the audit earns its quality.
   - Show the drafts grouped by topic. For each, ask the gap: *why this over the alternatives, what
     was actually considered, and has it since been revised?*
   - Batch clean forks with `AskUserQuestion`; leave room for "don't remember" — if the user can't
     recall, keep the decision but mark `rationale` as inferred ("inferred from the code; original
     reasoning not recorded") rather than fabricating one.
   - Correct the draft from their answers: fix chosen option, drop wrong alternatives, set real
     criteria, add `history` for anything they say was changed.

**5. Write + regenerate.** Only after approval, create each `decisions/NNNN-slug.json` (sequential
ids from the next free number; option ids `o<N><a..>`), reusing criterion wording verbatim across
decisions. Regenerate the viewer **once**, at the end, not per decision:

```
python3 .claude/skills/decision-tree/generate.py decisions decisions/graph.html
```

## Detection recipes
Signals → candidate decision. Read the file to confirm before drafting; don't assume from presence.

| Signal (file / command) | Candidate decision | Title (plain) |
|---|---|---|
| `package.json`, `tsconfig.json` `strict` | Language & strictness (JS vs TS, strict on/off) | "What language the app is written in" |
| `package.json` deps: react / vue / svelte / angular / next / expo | Primary framework | "What the app is built with" |
| `requirements.txt` / `pyproject.toml` / `go.mod` / `Gemfile` / `pom.xml` / `Cargo.toml` | Language & backend framework (django/flask/fastapi/rails/spring/gin) | "What the backend is built with" |
| ORM / driver: `prisma`, `drizzle`, `sequelize`, `pg`, `mysql2`, `sqlite3`, `mongoose`, `sqlalchemy` | Data store + access layer | "Where data is stored" |
| `*.prisma`, `migrations/`, `schema.sql` | Data model / schema ownership | "How the database is structured" |
| auth deps: `next-auth`, `passport`, `@clerk`, `firebase-auth`, `jsonwebtoken`, `bcrypt` | Auth / identity | "How users sign in" |
| `schema.graphql`, `apollo`, route files, `openapi.*` | API style (REST / GraphQL / RPC) | "How the front and back ends talk" |
| state libs: `redux`, `zustand`, `jotai`, `mobx`, `@tanstack/query` | State management | "How app state is managed" |
| styling: `tailwind.config`, `styled-components`, `*.module.css`, `@emotion` | Styling approach | "How the app is styled" |
| `vite.config`, `webpack.config`, `next.config`, `rollup`, `esbuild` | Build / bundler tooling | "How the app is built and bundled" |
| `Dockerfile`, `vercel.json`, `netlify.toml`, `fly.toml`, `serverless.yml`, `*.tf` | Hosting / deployment target | "Where the app runs" |
| `.github/workflows/`, `.gitlab-ci.yml`, `circleci/` | CI / release strategy | "How changes are tested and shipped" |
| test deps: `jest`, `vitest`, `playwright`, `cypress`, `pytest`, `rspec` | Testing strategy | "How the app is tested" |
| `pnpm-workspace.yaml`, `turbo.json`, `nx.json`, `lerna.json`, multiple `package.json` | Repo structure (monorepo vs single) | "How the code is organized into packages" |
| `git log --diff-filter=D` of a manifest dep; "migrate/switch/replace" in `git log --oneline` | A **reversal** — draft with a `history` entry | (topic of the swap) |

Tailor the list to the actual stack — these are the common cases, not a fixed set. If the repo is
in a language not above, infer the equivalent slots (its manifest, framework, data layer, deploy).

## Interview rules
- Ask only the gaps the scan **couldn't** determine — never re-ask what the code already proves.
- One topic per question; offer the inferred alternatives as the options so the user just picks/edits.
- Prefer `AskUserQuestion` for the why-over-alternatives forks; recommend the option the evidence
  points to (first, marked "Recommended") but let the user override.
- If the user doesn't recall the reasoning, keep the decision and mark the rationale inferred —
  a recorded choice with an honest "why unknown" beats a fabricated rationale.
