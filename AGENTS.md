# Tap working agreement

Read `README.md` and `LOG.md`. This is the neutral `ricardo-calcina/homebrew-tap` repository (`ricardo-calcina/tap` to Homebrew), separate from the Khuluma source repository. The canonical checkout folder is `homebrew-tap`, beside `khuluma`; isolated task worktrees can use other folder names.

`Formula/khuluma.rb` is the canonical CLI formula; root `formula_renames.json` maps the former `tmux-whisper` name to it. `.github/workflows/homebrew-qa.yml` owns manual disposable release QA; `release/` retains its script, runbook and exact v0.9/v0.10 fixtures. Keep one active formula, map and workflow. Never use a placeholder checksum or reuse a legacy archive checksum for renamed code; verify the actual immutable source tag/archive before updating the formula.

Preserve public release history and user data. A formula installs CLI code and native source; it does not install Khuluma.app, migrate a profile, warm a daemon or change Keychain. Use static checks during preparation; run release, Homebrew installation/upgrade and publication only in the authorized release workflow. Keep current work in `LOG.md`; do not create a second task tracker.
