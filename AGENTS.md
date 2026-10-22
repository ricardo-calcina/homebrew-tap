# Tap working agreement

Read `README.md` and `LOG.md`. This is the neutral `ricardo-nth/homebrew-tap` repository (`ricardo-nth/tap` to Homebrew), separate from the Khuluma source repository. The canonical checkout folder is `homebrew-tap`, beside `khuluma`; isolated task worktrees can use other folder names.

The active formula still tracks the published legacy v0.9.0 CLI. The canonical Khuluma v0.10.0 candidate and rename map are staged under `release/` until the final source archive exists and its actual SHA256 has been verified. Never put a placeholder checksum in `Formula/`, activate the root rename map before the new formula, or reuse the legacy archive checksum for renamed code.

Preserve public release history and user data. A formula installs CLI code and native source; it does not install Khuluma.app, migrate a profile, warm a daemon or change Keychain. Use static checks during preparation; run release, Homebrew installation/upgrade and publication only in the authorized release workflow. Keep current work in `LOG.md`; do not create a second task tracker.
