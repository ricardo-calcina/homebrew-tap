The release formula is `Formula/khuluma.rb`, with root `formula_renames.json`
mapping the former package name to it. The sole manual workflow is
`.github/workflows/homebrew-qa.yml`; obsolete staging copies were retired after
candidate QA passed. Actual runner outcomes are recorded separately in LOG.md.
The earlier [transport bridge](https://github.com/ricardo-nth/homebrew-tap/pull/1) refreshed only the old v0.9.0 same-tag archive URL/checksum after the source repository rename.

GitHub's standard hosted runners are free for public repositories; larger
runners remain charged even for public repositories. The candidate allocates
only the literal standard `macos-latest` label, refuses private repositories at
job allocation, and has no cache or artifact-upload step. It needs no second VM
on the user's 8 GB Mac. The current reference lists standard Apple Silicon
macOS runners at 3 cores/7 GB, sufficient for this copy-only formula QA; runner
image details can change. [GitHub runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners),
[GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

Initial GitHub repository metadata was checked read-only on 2026-10-22:
`ricardo-nth/homebrew-tap` is public, its default branch is main, and it had no
existing `.github` workflow to extend. The workflow now has three independent disposable scenarios: `fresh`, `upgrade-v0.9` and `upgrade-v0.10`, with at most two standard public macOS VMs at once. It uses checkout with
`clean:false` and no persisted credentials, contents-read permission, and a
35-minute job limit. It dispatches only when explicitly requested with final inputs.

Homebrew requires the renamed file/class and the old-to-new
`formula_renames.json` mapping in the same tap; do not leave two active formulae
for one package. Migration moves the installed old keg and updates its links;
it does not install the newer source. Therefore the v0.9 upgrade job runs actual
`brew migrate` followed by actual `brew upgrade`, with assertions between them.
It refuses a pre-existing canonical rack, avoiding the migrator's conflict
deletion path. [Homebrew rename instructions](https://docs.brew.sh/Rename-A-Formula),
[Homebrew migrator implementation](https://docs.brew.sh/rubydoc/Migrator.html#migrate-instance_method).

Current Homebrew requires canonical formula trust when an old name migrates to
a new formula; old-name trust does not transfer. The upgrade fixture explicitly
runs `brew trust --formula ricardo-nth/tap/khuluma` only after installing the
reviewed candidate into its private fixture tap. Its trust store belongs to the
synthetic HOME and explicitly confined XDG_CONFIG_HOME; inherited Homebrew config
overrides are discarded. No daily Mac trust is changed. Doctor source routes may include
`libexec/../share`; QA requires the resolved directory and existing Package.swift
to identify the same canonical keg, rather than comparing lexical spellings.
[Homebrew tap trust](https://docs.brew.sh/Tap-Trust).

Inputs required at the actual release gate

The v0.11.0 candidate uses verified immutable commit
`31b86a65a4b2b9b2c32e1faf51af81f46bd93b1b` and measured archive SHA256
`ddac91098b8e616bf9edfa526eae6ef8fe4fa347907634570589788642b2b9ee`.
All 192 regular archive files matched that Git commit, and the real pinned
bootstrap passed in a private child HOME with real user roots unchanged.
Three-scenario hosted package QA remains required before publication.

The earlier completed v0.10.0 candidate used commit
`f8af27e95c6763b30b52da107da3120c4d96f190` and actual archive SHA256
`a0402bb36e3e0e86686cd0e4627afd5bbdb954e5e971e69cf06ac7caa6ea17b0`.
The renamed v0.9.0 archive SHA256 is
`61cc4d746734cb1c61146b1b086d1f381e701cd1a8b04f242ddfb2ecb81d85f2`.
Both candidate scenarios passed before the tracked formula/map moves in
[run 39842673670](https://github.com/ricardo-nth/homebrew-tap/actions/runs/39842673670).
Both published-formula scenarios then passed at tap commit
`d0724ae9255cf1b47cd8b135dd8ded71abf635d2` with
`canonical_formula=Formula/khuluma.rb`: [run 39843684723](https://github.com/ricardo-nth/homebrew-tap/actions/runs/39843684723),
Homebrew 7.0.9/arm64. Both runs included strict audit, actual formula tests,
one canonical owner and unchanged synthetic profiles. Uninstall was not run.
For future releases, repeat against the exact published formula paths.

- A completed canonical formula inside this checkout, using the **actual final
  canonical tag URL and measured archive SHA256**. The default workflow path is
  `Formula/khuluma.rb`. An unresolved checksum is rejected. The workflow does not fill or
  guess its checksum, create a tag, or activate the formula/map.
- The exact commit of that final canonical source tag. QA resolves the public
  tag and checks this value, then fetches/verifies the archive bytes and required
  safe payload. No model or native/app product is downloaded or built.
- The measured SHA256 of the **same unchanged v0.9.0 tag** at the renamed source
  repository's archive URL. Historical commit
  `d0152e45f84551b71a679cfc32da0b9821d8f4f9` is preserved and checked by QA.

`fixtures/khuluma-v0.10.0.rb` retains the exact published v0.10 canonical formula for the direct upgrade scenario. Its source commit and archive checksum above remain immutable.

`fixtures/tmux-whisper-v0.9.0.rb` is the exact formula published before the source repository rename,
preserved with SHA256
`3b609395f1b31ec8c029116aa8708e3f5f52d463311964aa2a7cf3406662ba60`.
The upgrade fixture changes **only its URL and SHA256 lines** to the actual
renamed-repository v0.9.0 archive transport. GitHub's generated archive prefix
and bytes/checksum can change after repository rename. This fixture override
does not edit old tag code, dependencies, install body, class, version or test,
and it never changes the active legacy formula. It is not a checksum exception
for the new formula: the new formula must always use its actual final tag.

What the current jobs check

1. All scenarios verify public tag commits, actual archive SHA256s, a single safe source root, version declarations and required payload. Formula installation has no model, daemon, app or build hooks.
2. Each job creates a private fixture tap under the runner temporary root. Fresh install proves help/version/defaults do not create profile/data trees.
3. `upgrade-v0.9` installs the exact old formula (only renamed archive transport changes), retains its keg, then runs actual migration and upgrade. Its un-migrated legacy profile must remain unchanged and normal app-config must refuse it.
4. `upgrade-v0.10` installs the exact published canonical formula and retains its keg. It seeds a canonical config/vocab/usage profile, proves old app-config works, then requires the next version to read that same profile without byte, mode or mtime changes. No identity migration is needed.
5. Current command/opt/library links resolve to one canonical keg. The current keg must contain neither the old command nor its doctor adapter; old retained keg code is recovery material. The rename map remains package ownership metadata.
6. A separate contract fixture checks app contract 3, canonical socket, library API, native sources/tests/helpers/assets, doctor schema 2 and pkgshare source discovery. No daemon/model is loaded.
7. Strict audit and actual formula tests run with cleanup disabled and temporary retention. Package inventory has one canonical owner; real runner-home product roots remain absent. Uninstall is not run.

Recovery and execution boundaries

The script refuses a daily Mac and requires GitHub-hosted macOS runner context,
the expected public-tap workflow marker and repository. Every product child gets
an explicitly synthetic home/temp/config boundary; the invoking process's home
is not reassigned. Read-only metadata checks ensure the runner's original home
has no product roots and remains that way.

Homebrew automatic cleanup is disabled; install, upgrade and formula test use
`--keep-tmp`. The script performs no uninstall, cleanup, `rm`, `rmdir`, unlink,
git clean, forced Git reset or manual permanent removal. Originals are retained
by copies or exact moves. Normal package-manager link updates are the requested
genuine migration/upgrade; there is no conflicting canonical rack to merge.
No policy exception is invented for uninstall: that gate is replaced here by
inventory/owner and unchanged-profile checks and is reported as **not run**.
[Homebrew retention options](https://docs.brew.sh/Manpage),
[Homebrew cleanup behavior](https://docs.brew.sh/FAQ#how-do-i-keep-old-versions-of-a-formula-when-upgrading).

The runner prints a compact metadata report and adds a success note to its job
summary. Synthetic fixtures, downloaded source archives, old keg copies and
formula/test staging remain until GitHub naturally disposes the VM. They are
not uploaded, billed as artifacts, or promised as persistent recovery storage.
No real user data enters this VM. There is no daily-Mac uninstall/cleanup test.

Static local preparation can compile the Python source without executing it,
check the YAML and Ruby syntax, verify the preserved fixture hash and confirm
the template fails the input gate. `--check-only` validates a completed formula
and supplied hash/commit syntax without Brew, network or profile mutations; it
does not establish that a future archive exists or that Homebrew QA passed.
Actual release acceptance requires all three scenarios with the real final inputs.
