# Tap log

## Now

Preparing canonical-only v0.11.0 in an isolated worktree. The formula is bound to the verified immutable source tag at `31b86a65`; actual archive SHA is in `Formula/khuluma.rb`. The archive's 192 files matched Git and pinned bootstrap passed privately. Hosted fresh/v0.9/v0.10 package QA and publication are next. The daily app/local CLI refresh passed separately; no daily Brew changes yet.

The published v0.10 fresh/v0.9 QA outcomes remain in Done and the QA record. Keep prior releases and the exact v0.9/v0.10 fixtures intact.

The source [LOG](https://github.com/ricardo-nth/khuluma/blob/main/LOG.md) owns current product work; its [archived identity record](https://github.com/ricardo-nth/khuluma/blob/main/docs/plans/archive/KHULUMA_IDENTITY_RENAME.md) preserves migration evidence. Keep the neutral tap and one canonical formula/map. Package installation does not migrate user data or install the app.

## Next

- [ ] P1 · Bind the verified v0.11 source/archive, pass all three disposable scenarios and publish matching canonical-only package · added 2026-10-23

- [x] P1 · Verify the final source archive, activate canonical formula/rename map, test fresh install and old-formula upgrade in isolation, then publish the tap · added 2026-10-22

## Done

- 2026-10-23 · Prepared canonical-only formula and three-scenario QA against measured v0.11 source; prior fixtures retained · release/HOMEBREW_QA.md

- 2026-10-22 · Published canonical formula/map; fresh and genuine v0.9 upgrade passed strict audit, tests and ownership/data checks · #5; d0724ae; Actions39843684723
- 2026-10-22 · This Mac migrated/upgraded to v0.10.0 with cleanup disabled, old keg retained and daily runtime preserved · Formula/khuluma.rb

- 2026-10-22 · Restored v0.9 Brew archive transport after source rename; unchanged tag/payload verified · #1; 960c9f2

- 2026-10-22 · Added inactive disposable macOS fresh/old-formula upgrade QA; static checks passed, actual release inputs pending · 0bf77b8; release/HOMEBREW_QA.md

- 2026-10-22 · Prepared canonical formula and rename map outside active Formula; Ruby syntax and payload wiring checked; publication pending · release/

- 2026-10-22 · Outer source collection renamed Khuluma; tap folder, formula and Git identity retained · README.md
- 2026-10-22 · Moved with the complete collection under VPS/Apps/tmux-whspr; source sibling and formula retained · ../README.md
- 2026-10-22 · Corrected local formula-update path and documented CLI/app and repository boundaries; formula unchanged · README.md
