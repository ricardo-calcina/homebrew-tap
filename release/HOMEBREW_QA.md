The completed release candidate is `release/khuluma.rb`. The manual workflow
is `.github/workflows/homebrew-qa.yml`; `release/homebrew-qa.yml` retains the
original staging copy. Local preparation ran no Homebrew install, migration,
upgrade or uninstall. Actual runner outcomes are recorded separately in LOG.md.
The legacy v0.9.0 recipe remains active. A separate [transport bridge](https://github.com/ricardo-nth/homebrew-tap/pull/1) refreshed only its same-tag archive URL/checksum after the source repository rename; the candidate template/rename map remain inactive.

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
existing `.github` workflow to extend. This is one manual-only workflow with two independent disposable
runner jobs, `fresh` and `upgrade`, run sequentially. It uses checkout with
`clean:false` and no persisted credentials, contents-read permission, and a
35-minute job limit. It dispatches only when explicitly requested with final inputs.

Homebrew requires the renamed file/class and the old-to-new
`formula_renames.json` mapping in the same tap; do not leave two active formulae
for one package. Migration moves the installed old keg and updates its links;
it does not install the newer source. Therefore the upgrade job runs actual
`brew migrate` followed by actual `brew upgrade`, with assertions between them.
It refuses a pre-existing canonical rack, avoiding the migrator's conflict
deletion path. [Homebrew rename instructions](https://docs.brew.sh/Rename-A-Formula),
[Homebrew migrator implementation](https://docs.brew.sh/rubydoc/Migrator.html#migrate-instance_method).

Inputs required at the actual release gate

The completed v0.10.0 candidate uses commit
`f8af27e95c6763b30b52da107da3120c4d96f190` and actual archive SHA256
`a0402bb36e3e0e86686cd0e4627afd5bbdb954e5e971e69cf06ac7caa6ea17b0`.
The renamed v0.9.0 archive SHA256 is
`61cc4d746734cb1c61146b1b086d1f381e701cd1a8b04f242ddfb2ecb81d85f2`.
First dispatch with `canonical_formula=release/khuluma.rb`; after activation,
repeat against `Formula/khuluma.rb` to check the published formula.

- A completed canonical formula inside this checkout, using the **actual final
  canonical tag URL and measured archive SHA256**. The default workflow path is
  `Formula/khuluma.rb`; a completed candidate under release/ can be supplied before
  activation. The unresolved `.rb.in` is rejected. The workflow does not fill or
  guess its checksum, create a tag, or activate the formula/map.
- The exact commit of that final canonical source tag. QA resolves the public
  tag and checks this value, then fetches/verifies the archive bytes and required
  safe payload. No model or native/app product is downloaded or built.
- The measured SHA256 of the **same unchanged v0.9.0 tag** at the renamed source
  repository's archive URL. Historical commit
  `d0152e45f84551b71a679cfc32da0b9821d8f4f9` is preserved and checked by QA.

`fixtures/tmux-whisper-v0.9.0.rb` is the exact formula published before the source repository rename,
preserved with SHA256
`3b609395f1b31ec8c029116aa8708e3f5f52d463311964aa2a7cf3406662ba60`.
The upgrade fixture changes **only its URL and SHA256 lines** to the actual
renamed-repository v0.9.0 archive transport. GitHub's generated archive prefix
and bytes/checksum can change after repository rename. This fixture override
does not edit old tag code, dependencies, install body, class, version or test,
and it never changes the active legacy formula. It is not a checksum exception
for the new formula: the new formula must always use its actual final tag.

What the jobs check

1. Both jobs verify public tag commits, actual archive SHA256s, a single safe
   source root, exact old/new CLI version declarations and required payload.
   Only dependency bottles for ffmpeg and Python are installed. The formula's
   install body is checked to exclude runtime/build hooks.
2. Each job creates a private fixture tap under a private runner temporary root,
   using the real `ricardo-nth/tap` identity with a local Git remote. No tap was
   previously installed on that VM. The fresh job installs canonical source
   into an empty synthetic home and proves help/version/defaults create no
   profile/data tree.
3. The upgrade job genuinely installs v0.9.0 from the preserved old formula,
   runs its version probe, retains the exact old keg outside Cellar, installs
   the new formula/map into that same tap and commits the local fixture change.
   It then migrates, proves v0.9 remains under the canonical rack, upgrades,
   and proves final opt/bin/shim/library links share the canonical current keg.
   Old opt must point at that same keg; the old-name rack may remain an alias.
4. Both jobs retain a synthetic old config/vocab/usage profile and prove the
   package install/upgrade does not change its bytes, mode or mtime. Canonical
   and legacy wrappers must return equal version JSON, canonical identity, and
   migration_required=true. An attempted normal app-config probe must refuse
   that un-migrated profile without creating an empty canonical profile.
5. A separate retained contract profile checks app contract 3, canonical socket,
   library API marker, native sources/tests/helpers/assets, doctor schema 2,
   legacy doctor adapter and pkgshare native-source discovery. Pure probes must
   leave this fixture unchanged. No daemon endpoint/model/build is needed.
6. Strict audit and the actual formula test run with temporary retention.
   Package inventory must belong only to the canonical rack, physical product
   rack ownership must be singular, and real runner-home product roots remain
   absent. This proves packaging ownership without deleting the payload.

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
Actual release acceptance requires both runner jobs with the real final inputs.
