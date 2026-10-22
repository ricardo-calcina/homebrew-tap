# Tap log

## Now

Canonical-only v0.11.0 is published in #7 at `449aa971`. Its formula is bound to immutable source commit `31b86a65`; all 192 archive files matched Git and the actual checksum is in `Formula/khuluma.rb`. Pinned bootstrap, candidate QA [39852559290](https://github.com/ricardo-nth/homebrew-tap/actions/runs/39852559290) and published QA [39853338244](https://github.com/ricardo-nth/homebrew-tap/actions/runs/39853338244) passed. Each hosted run passed fresh install, v0.9 upgrade and v0.10 upgrade, including strict audit, actual formula tests, one owner and unchanged synthetic profiles.

This Mac's targeted v0.10→v0.11 Brew upgrade passed with automatic updates and cleanup disabled. The v0.9/v0.10 kegs remain; dependencies, trust, canonical config/model and running daily app/daemon were preserved. Local and Brew CLIs both select the same profile. The user accepted the separately refreshed v0.11 app.

The source [LOG](https://github.com/ricardo-nth/khuluma/blob/main/LOG.md) owns product work; its [archived identity record](https://github.com/ricardo-nth/khuluma/blob/main/docs/plans/archive/KHULUMA_IDENTITY_RENAME.md) preserves migration evidence. Keep the neutral tap, one canonical formula/map and exact historical fixtures. Package installation does not migrate user data or install the app. Earlier QA failures were followed by successful runs; no outstanding failure remains for this release.

## Next

- [x] P1 · Bind the verified v0.11 source/archive, pass all three disposable scenarios and publish matching canonical-only package · added 2026-10-23

- [x] P1 · Verify the final source archive, activate canonical formula/rename map, test fresh install and old-formula upgrade in isolation, then publish the tap · added 2026-10-22

## Done

- 2026-10-23 · Published v0.11 and passed all three candidate/published QA scenarios plus the retained local upgrade · #7; Actions39853338244

- 2026-10-23 · Prepared canonical-only formula and three-scenario QA against measured v0.11 source; prior fixtures retained · release/HOMEBREW_QA.md

- 2026-10-22 · Published canonical formula/map; fresh and genuine v0.9 upgrade passed strict audit, tests and ownership/data checks · #5; d0724ae; Actions39843684723
- 2026-10-22 · This Mac migrated/upgraded to v0.10.0 with cleanup disabled, old keg retained and daily runtime preserved · Formula/khuluma.rb

- 2026-10-22 · Restored v0.9 Brew archive transport after source rename; unchanged tag/payload verified · #1; 960c9f2

- 2026-10-22 · Added inactive disposable macOS fresh/old-formula upgrade QA; static checks passed, actual release inputs pending · 0bf77b8; release/HOMEBREW_QA.md

- 2026-10-22 · Prepared canonical formula and rename map outside active Formula; Ruby syntax and payload wiring checked; publication pending · release/

- 2026-10-22 · Outer source collection renamed Khuluma; tap folder, formula and Git identity retained · README.md
- 2026-10-22 · Moved with the complete collection under VPS/Apps/tmux-whspr; source sibling and formula retained · ../README.md
- 2026-10-22 · Corrected local formula-update path and documented CLI/app and repository boundaries; formula unchanged · README.md
