# Khuluma Homebrew tap

The neutral tap remains `ricardo-nth/tap`, hosted in `ricardo-nth/homebrew-tap`. Khuluma's canonical CLI formula is being prepared as `khuluma`; this checkout does not publish it yet. The existing active `Formula/tmux-whisper.rb` still installs the tagged v0.9.0 CLI with its original archive and checksum. It does not install Khuluma.app.

The local checkout layout is sibling folders `khuluma` and `homebrew-tap`, each with its own Git history. Earlier documentation's `tmux-whsper-brew-tap` spelling is the legacy checkout folder, not the Homebrew tap namespace.

## Current published CLI

Until the canonical release is published, the active formula remains available through:

```bash
brew tap ricardo-nth/tap
brew install ricardo-nth/tap/tmux-whisper
```

Its checked-in version is v0.9.0. This preparation pass did not check an online release or the installed version.

## Canonical release being prepared

The release target is v0.10.0 from `ricardo-nth/khuluma`. After its final source archive, formula and rename map are validated and published, the canonical install command will be:

```bash
brew install ricardo-nth/tap/khuluma
```

The CLI package includes `khuluma`, its matching libraries, the pinned native `khulumad` sources, Finder handler, recovery and migration helpers, defaults and assets. A temporary `tmux-whisper` command forwards to that same implementation for existing integrations. The formula declares the existing Python and ffmpeg runtime requirements; first daemon warmup also needs Apple Command Line Tools with Swift 6 support.

The formula does not create or migrate configuration, download models, warm the daemon, install a Finder action, create a signing certificate or install Khuluma.app during `brew install`. New default data paths use `khuluma`. Existing legacy data requires the [coordinated identity migration](../khuluma/docs/INTEGRATIONS.md#identity-migration), also shipped at the installed `share/khuluma/docs/INTEGRATIONS.md`. No portable automatic legacy-upgrade coordinator ships; apply/resume/rollback require a reviewed active coordinator; preserve old data and the working daily installation until the replacement passes its cutover checks. `khuluma version --json` reports canonical identity without starting the daemon.

## Release staging

- `release/khuluma.rb.in` is the complete candidate formula. Its SHA256 token is deliberately unresolved and it is outside `Formula/`.
- `release/formula_renames.json` is the prepared `tmux-whisper` → `khuluma` map. It stays outside the repository root until the canonical formula is ready in the same change.
- `release/HOMEBREW_QA.md` describes the inactive disposable public macOS workflow and its real old-to-new upgrade gates. Static preparation passed; no runner job has run.
- `Formula/tmux-whisper.rb` remains unchanged while the candidate is pending. Its old description and paths describe the old release; they are not a template for the new package.

To activate the prepared release, finish and tag the source first. Fetch the actual `ricardo-nth/khuluma` v0.10.0 archive, inspect its safe root and payload, verify the release version, and compute its SHA256. Do not reuse the old checksum or guess a hash from the Git tree. Replace the candidate's SHA256 token with those verified bytes and place the completed file at `Formula/khuluma.rb` only when it is valid. Then place the rename map at the repository root, remove the superseded active legacy formula as part of that same reviewed release change, and validate the upgrade path before publishing.

The source updater can refresh URL and checksum on an already completed canonical formula:

```bash
# From the source checkout; this downloads an archive and changes the tap file.
tools/update-homebrew-formula.sh v0.10.0 --write --formula ../homebrew-tap/Formula/khuluma.rb
```

It updates only URL and SHA256. It does not rename a formula, update its class/install paths/caveats/tests, activate the rename map or publish anything.

## Validation and publication

Preparation checks Ruby syntax, JSON and source payload wiring. Before publication, use the actual final archive for `brew audit --strict ricardo-nth/tap/khuluma`, formula tests and a fresh install in a disposable macOS/Homebrew environment. Separately test upgrade/migration from installed v0.9.0, canonical and compatibility commands, native source/pkgshare discovery, local-versus-Brew precedence, Finder handler resolution, package ownership, unchanged user data and rollback. Uninstall is not run under the recovery-only cleanup agreement; the QA records that limitation. Test commands in this paragraph are future release gates; they were not run during this preparation.

Commit and push the tap separately from the source after the release checks pass and publication is authorized. Keep the neutral tap identity; this change does not migrate users to another tap. Public history and dated archived documentation remain intact.
