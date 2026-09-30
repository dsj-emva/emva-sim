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
4. Follow sections 1 and 3 of `../emva-app/docs/START_HERE.md` (including its skills and helper agents rules),
   and its section for the phase you are in (phase S, then phase 4).

`CONTEXT.md`, `docs/adr/` and `docs/START_HERE.md` are the only parts of `emva-app` this repository may
read, and nothing in `emva-app` is ever written. Never read or ask for Emva's code, and never write a profile
or generator from knowledge of how Emva's model works: the synthetic test must not be written in the model's
own hand.

## The guard hook

`.claude/hooks/guard_emva_app.py` runs before every Read, Grep, Glob, Edit, Write and Bash call and refuses
any that reaches into `emva-app` other than those three reads, by absolute or relative path, including shell
commands that mention the folder. It blocks ordinary and accidental reads, not deliberate workarounds (a script
that builds the path itself gets past it), so the rule above still binds. If the hook cannot run (no `uv`), it
refuses every call rather than letting it through. Its tests are in `tests/test_guard_emva_app.py`.

Start sessions with `claude --add-dir ../emva-app`. Without it, Claude Code's own check refuses every shell
command on a file outside this folder, so `cat ../emva-app/CONTEXT.md` fails even though the hook allows it (the
Read tool still works). The `additionalDirectories` setting would be the persistent way, but Claude Code
ignored it in headless runs (tested with relative, `~/` and absolute paths).

## How this repository talks to Emva

Only as the outside world does: files uploaded to Emva (CSV exports), and Emva's intake and CRM-update
endpoints over HTTP. No imports from, and no shared code with, `emva-app`.

## Working rules

- Helper agents here never read `emva-app` beyond `CONTEXT.md`, `docs/adr/` and `docs/START_HERE.md`.
- Tests first. Small commits, each ending with the co-author line the tooling asks for. The user merges; no
  agent pushes to `main`.
- Every number from synthetic data is labelled "on simulated data".
- Generated datasets and hidden truth are output, never committed (see `.gitignore`).
- No speculative options, no dead code, no commented-out code.

## Commands

- `make install`, `make test`, `make lint`.
- Python 3.12 is uv-managed (`uv python install 3.12`); the `/usr/local/bin/python3` on this machine is an
  unusable x86 build.
