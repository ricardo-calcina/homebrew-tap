# Tap log

## Now

Prepare the canonical Khuluma formula in the isolated rename worktree. The active formula remains the published v0.9.0 CLI, with verified archive transport updated after the source repository rename; `release/` holds the v0.10.0 template and formula rename map until the final source tag/archive and actual checksum exist. The source [rename plan](../khuluma/docs/KHULUMA_RENAME_PLAN.md) owns coordinated cutover and release gates; the final sibling checkout is `khuluma`.

## Next

- [ ] P1 · Verify the final source archive, activate canonical formula/rename map, test fresh install and old-formula upgrade in isolation, then publish the tap · added 2026-10-22

## Done

- 2026-10-22 · Restored v0.9 Brew archive transport after source rename; unchanged tag/payload verified · #1; 960c9f2

- 2026-10-22 · Added inactive disposable macOS fresh/old-formula upgrade QA; static checks passed, actual release inputs pending · 0bf77b8; release/HOMEBREW_QA.md

- 2026-10-22 · Prepared canonical formula and rename map outside active Formula; Ruby syntax and payload wiring checked; publication pending · release/

- 2026-10-22 · Outer source collection renamed Khuluma; tap folder, formula and Git identity retained · README.md
- 2026-10-22 · Moved with the complete collection under VPS/Apps/tmux-whspr; source sibling and formula retained · ../README.md
- 2026-10-22 · Corrected local formula-update path and documented CLI/app and repository boundaries; formula unchanged · README.md
