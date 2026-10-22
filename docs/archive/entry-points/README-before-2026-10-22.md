# homebrew-tap

Homebrew tap for `tmux-whisper`.

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
tools/update-homebrew-formula.sh vX.Y.Z --write --formula ../homebrew-tap/Formula/tmux-whisper.rb
```

That command downloads the tagged GitHub tarball, computes the Homebrew `sha256`, and updates the formula in place.
