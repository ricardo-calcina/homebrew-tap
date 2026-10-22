# Khuluma Homebrew tap

The neutral tap remains `ricardo-nth/tap`, hosted in `ricardo-nth/homebrew-tap`. Its canonical `khuluma` formula installs the v0.11.0 CLI from `ricardo-nth/khuluma`. It does not install Khuluma.app.

The local checkout layout is sibling folders `khuluma` and `homebrew-tap`, each with its own Git history. Earlier documentation's `tmux-whsper-brew-tap` spelling is the legacy checkout folder, not the Homebrew tap namespace.

## Install

```bash
brew tap ricardo-nth/tap
brew install ricardo-nth/tap/khuluma
```

For an installed v0.9.0 package, update the tap and trust the canonical formula before migrating package ownership and upgrading:

```bash
brew update
brew trust --formula ricardo-nth/tap/khuluma
brew migrate ricardo-nth/tap/tmux-whisper
brew upgrade ricardo-nth/tap/khuluma
```

Current Homebrew requires trust in the canonical formula; old-name trust does not transfer. This package migration does not migrate the user's profile. The former formula name is an alias to the same canonical package, rather than a second active formula.

## Package and user data

The CLI package includes `khuluma`, its matching libraries, the pinned native `khulumad` sources, Finder handler, recovery and migration helpers, defaults and assets. v0.11 removes the old command and doctor adapter; current integrations must call `khuluma`. Obsolete `DICTATE_*` and Lowkey signing overrides are rejected before writes. The formula declares the existing Python and ffmpeg runtime requirements; first daemon warmup also needs Apple Command Line Tools with Swift 6 support.

The formula does not create or migrate configuration, download models, warm the daemon, install a Finder action, create a signing certificate or install Khuluma.app during `brew install`. New default data paths use `khuluma`. Coming from the Lowkey app requires the completed v0.10 app/preferences/folder handoff before v0.11, which has no automatic legacy app imports. Existing legacy data requires the [coordinated identity migration](https://github.com/ricardo-nth/khuluma/blob/main/docs/INTEGRATIONS.md#identity-migration), also shipped at the installed `share/khuluma/docs/INTEGRATIONS.md`. No portable automatic legacy-upgrade coordinator ships; apply/resume/rollback require a reviewed active coordinator; preserve old data and the working daily installation until the replacement passes its cutover checks. `khuluma version --json` reports canonical identity without starting the daemon.

## Release maintenance

- `Formula/khuluma.rb` is the sole active formula, pinned to the actual final source archive and measured checksum.
- Root `formula_renames.json` maps `tmux-whisper` to `khuluma` in this same neutral tap.
- `.github/workflows/homebrew-qa.yml` runs the manual disposable public macOS fresh/v0.9-upgrade/v0.10-upgrade checks described in `release/HOMEBREW_QA.md`; LOG.md records actual outcomes.
- `release/fixtures/khuluma-v0.10.0.rb` preserves the exact published canonical formula for direct upgrade QA.
- `release/fixtures/tmux-whisper-v0.9.0.rb` preserves the exact original old formula for genuine upgrade QA. The earlier [transport bridge](https://github.com/ricardo-nth/homebrew-tap/pull/1) changed only its published archive URL/checksum after the source repository rename.

For each release, finish and tag the source first. Fetch the actual final-tag archive, inspect its safe root and payload, verify the release version, and compute its SHA256. Do not reuse an old checksum or guess a hash from the Git tree. Run all three disposable QA scenarios before publication, then repeat against the published formula. Keep formula renames and their map in the same reviewed change.

The source updater can refresh URL and checksum on an already completed canonical formula:

```bash
# From the source checkout; this downloads an archive and changes the tap file.
tools/update-homebrew-formula.sh v0.11.0 --write --formula ../homebrew-tap/Formula/khuluma.rb
```

It updates only URL and SHA256. It does not rename a formula, update its class/install paths/caveats/tests, activate the rename map or publish anything.

## Validation and publication

Preparation checks Ruby syntax, JSON and source payload wiring. Before publication, use the actual final archive for `brew audit --strict ricardo-nth/tap/khuluma`, formula tests and a fresh install in a disposable macOS/Homebrew environment. Separately test upgrade/migration from installed v0.9.0 and direct canonical v0.10.0 upgrade, canonical commands and current old-command absence, native source/pkgshare discovery, local-versus-Brew precedence, Finder handler resolution, package ownership, unchanged user data and rollback. Uninstall is not run under the recovery-only cleanup agreement; the QA records that limitation. The earlier v0.10 candidate fresh-install and genuine v0.9.0 migrate/upgrade checks passed on Homebrew 7.0.9 (Apple Silicon), including strict audit and actual formula tests: [run 39842673670](https://github.com/ricardo-nth/homebrew-tap/actions/runs/39842673670). Published-formula verification is recorded in `LOG.md`. The v0.11.0 fresh/v0.9/v0.10 scenarios all passed for both the candidate and published formula; [published run 39853338244](https://github.com/ricardo-nth/homebrew-tap/actions/runs/39853338244) records the final package gate.

Commit and push the tap separately from the source after the release checks pass and publication is authorized. Keep the neutral tap identity; this change does not migrate users to another tap. Public history and dated archived documentation remain intact.
