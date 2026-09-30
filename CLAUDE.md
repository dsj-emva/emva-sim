# emva-sim

This repository builds, for testing Emva from the outside:

- **Industry profiles**: every industry-specific fact, each uncertain number a range tagged sourced, estimated or
  guessed, with its source.
- **The generator**: synthetic datasets in the shape a real sales system export would have (not Emva's
  standard shape), with realistic mess, generated at the low, middle and high ends of every range.
- **The lead simulator**: sends leads and plays a realistic sales team on a simulated clock, then grades Emva's
  scores against the hidden truth. The hidden truth and the grading stay here.

## Every session

1. Read this file.
2. Read `../emva-app/CONTEXT.md` and use its words exactly (Industry profile, Lead simulator, Simulated clock,
   Hidden truth, Stage, Canonical ladder, Trust gate, ...). If a word you need is missing, or you want to use a
   word it says to avoid, stop and ask.
3. Follow decision 0007 (`../emva-app/docs/adr/0007-industry-profiles-are-ranges.md`), and read the other
   decisions in `../emva-app/docs/adr/` the task touches.

Those two are the only parts of `emva-app` this repository may read; `.claude/settings.json` denies the rest.
Never read or ask for Emva's code, and never write a profile or generator from knowledge of how Emva's model
works: the synthetic test must not be written in the model's own hand.

## How this repository talks to Emva

Only as the outside world does: files uploaded to Emva (CSV exports), and Emva's intake and CRM-update
endpoints over HTTP. No imports from, and no shared code with, `emva-app`.

## Skills and helper agents

These follow section 3 of `emva-app/docs/START_HERE.md`, which this repository cannot read:

- Use a skill wherever one fits instead of working it out from scratch: `/tdd` for every feature and fix,
  `/code-review` on every branch before it is handed over, `/research` for industry profiles and anything that
  needs cited sources, `/diagnose` for any bug, failing test or slowdown, `/to-prd` and `/to-issues` at the start
  of a phase. If a skill is not installed, say so and carry on without it; never invent one.
- Hand searches, reviews, research and independent parallel tasks to helper agents; keep the main session for
  decisions, talking to the user and putting results together. Tell each helper agent what to read, give it a
  self-contained task, and check its findings before acting on them. Helper agents here never read `emva-app`
  beyond `CONTEXT.md` and `docs/adr/`.

## Working rules

- Tests first. Small commits, each ending with the co-author line the tooling asks for. The user merges; no
  agent pushes to `main`.
- Every number from synthetic data is labelled "on simulated data".
- Generated datasets and hidden truth are output, never committed (see `.gitignore`).
- No speculative options, no dead code, no commented-out code.

## Commands

- `make install`, `make test`, `make lint`.
- Python 3.12 is uv-managed (`uv python install 3.12`); the `/usr/local/bin/python3` on this machine is an
  unusable x86 build.
