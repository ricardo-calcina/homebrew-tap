# Tmux Whisper Homebrew tap

Homebrew tap for `tmux-whisper`. The local directory is `tmux-whsper-brew-tap`, beside `tmux-whisper`; each is a separate Git repository.

The checked-in formula points to `v0.9.0` as of the 2026-10-22 source inspection. That is a recorded formula version, not an online release or installed-version check. It installs the CLI, not Khuluma.app. Khuluma's current source and daily-app instructions are in [`../tmux-whisper/README.md`](../tmux-whisper/README.md).

## Install

```bash
brew tap ricardo-nth/tap
brew install ricardo-nth/tap/tmux-whisper
```

## Upgrade

```bash
brew update
brew upgrade tmux-whisper
```

## Formula

- `Formula/tmux-whisper.rb`

## Updating the Formula

From the source repo checkout:

```bash
tools/update-homebrew-formula.sh vX.Y.Z --write --formula ../tmux-whsper-brew-tap/Formula/tmux-whisper.rb
```

That command downloads the tagged GitHub tarball, computes the Homebrew `sha256`, and updates the formula in place.

The updater's default path remains `../homebrew-tap`; the explicit `--formula` above is required for this workspace. Fixing the script is pending source-maintainer work in the source repository's `LOG.md`. Updating the formula downloads an archive; committing, pushing and publishing require the release workflow and authorization. A docs-only pass does not run these commands.
