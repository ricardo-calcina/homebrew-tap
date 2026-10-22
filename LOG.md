# Tap log

## Now

The canonical v0.10.0 CLI formula and same-tap rename map are published. Source tag `v0.10.0` is pinned to `f8af27e`; measured archive SHA is in `Formula/khuluma.rb`. Both published fresh-install and genuine v0.9.0 migrate/upgrade jobs passed strict audit, formula tests, singular package ownership and unchanged-profile checks on Homebrew 7.0.9/arm64. This Mac also migrated and upgraded with old code/recovery retained; the daily app is a separate installation.

The source [LOG](https://github.com/ricardo-nth/khuluma/blob/main/LOG.md) owns current product work; its [archived identity record](https://github.com/ricardo-nth/khuluma/blob/main/docs/plans/archive/KHULUMA_IDENTITY_RENAME.md) preserves migration evidence. Keep the neutral tap and one canonical formula/map. Package installation does not migrate user data or install the app.

## Next

- [x] P1 · Verify the final source archive, activate canonical formula/rename map, test fresh install and old-formula upgrade in isolation, then publish the tap · added 2026-10-22

## Done

- 2026-10-22 · Published canonical formula/map; fresh and genuine v0.9 upgrade passed strict audit, tests and ownership/data checks · #5; d0724ae; Actions39843684723
- 2026-10-22 · This Mac migrated/upgraded to v0.10.0 with cleanup disabled, old keg retained and daily runtime preserved · Formula/khuluma.rb

- 2026-10-22 · Restored v0.9 Brew archive transport after source rename; unchanged tag/payload verified · #1; 960c9f2

- 2026-10-22 · Added inactive disposable macOS fresh/old-formula upgrade QA; static checks passed, actual release inputs pending · 0bf77b8; release/HOMEBREW_QA.md

- 2026-10-22 · Prepared canonical formula and rename map outside active Formula; Ruby syntax and payload wiring checked; publication pending · release/

- 2026-10-22 · Outer source collection renamed Khuluma; tap folder, formula and Git identity retained · README.md
- 2026-10-22 · Moved with the complete collection under VPS/Apps/tmux-whspr; source sibling and formula retained · ../README.md
- 2026-10-22 · Corrected local formula-update path and documented CLI/app and repository boundaries; formula unchanged · README.md
