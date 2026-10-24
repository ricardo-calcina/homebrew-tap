class Khuluma < Formula
  desc "Local macOS dictation back end and audio file transcription CLI"
  homepage "https://github.com/ricardo-calcina/khuluma"
  url "https://github.com/ricardo-calcina/khuluma/archive/refs/tags/v0.11.0.tar.gz"
  sha256 "ddac91098b8e616bf9edfa526eae6ef8fe4fa347907634570589788642b2b9ee"
  license "MIT"

  depends_on "ffmpeg"
  depends_on macos: :sonoma
  depends_on "python@3.15"

  def install
    # Keep the executable beside its matching libraries.
    libexec.install "bin/khuluma", "bin/khuluma-lib.sh", "bin/khuluma-lib"
    runtime_environment = {
      KHULUMA_LIB_PATH:         libexec/"khuluma-lib.sh",
      KHULUMA_INTERNAL_LIB_DIR: libexec/"khuluma-lib",
      PATH:                     "#{formula_opt_libexec("python@3.15")}/bin:#{formula_opt_bin("ffmpeg")}:$PATH",
    }
    (bin/"khuluma").write_env_script libexec/"khuluma", runtime_environment
    bin.install_symlink libexec/"khuluma-lib.sh" => "khuluma-lib.sh"

    # The daemon is built in a user-writable runtime tree on first warmup.
    # Ship the pinned manifest plus Sources/Tests; never build or initialize a
    # user's models, profile, services or application bundle during brew install.
    pkgshare.install "config", "integrations", "assets", "tools", "native"
    pkgshare.install "install.sh", "bootstrap.sh", "README.md", "CHANGELOG.md"
    (pkgshare/"docs").install "docs/INTEGRATIONS.md"
  end

  def caveats
    <<~EOS
      This formula installs the CLI and native daemon source, not Khuluma.app.
      First warmup needs the Apple Command Line Tools with Swift 6 support.
      A local Parakeet CoreML model is required; installation does not download it.
      Place it under ~/.local/share/khuluma/models or set swift_parakeet.model_path.
      Existing custom model paths stay in use.

      New profiles use ~/.config/khuluma. Models and native builds use
      ~/.local/share/khuluma; optional sounds use ~/.local/share/sounds/khuluma.
      XDG and supported KHULUMA_* overrides remain available.

      Lowkey app users must first complete the coordinated v0.10.0 app,
      preferences and folder handoff. v0.11.0 does not automatically import
      legacy app folders or preference keys.

      Existing Tmux Whisper users must complete the controlled identity migration
      before writing through the new CLI. The CLI refuses to create an unrelated
      empty default profile over an existing legacy installation. Start with the
      read-only migration plan; do not run install.sh over your daily runtime:

        #{opt_pkgshare}/tools/migrate-khuluma-identity.sh --dry-run

      Operator handoff and recovery: #{opt_pkgshare}/docs/INTEGRATIONS.md
      Apply/resume/rollback need a reviewed active coordinator; no portable
      automatic legacy-upgrade coordinator ships. Never manufacture receipts.

      Check the selected installation without starting its daemon:

        khuluma version --json
        khuluma doctor

      Configuration, history, vocabulary and models remain user-owned data.
    EOS
  end

  test do
    require "json"

    ENV["KHULUMA_CONFIG_DIR"] = (testpath/"profile").to_s
    ENV["XDG_DATA_HOME"] = (testpath/"data").to_s
    ENV["KHULUMA_INSTALL_WARMUP"] = "0"
    assert_match "khuluma: the back end for Khuluma", shell_output("#{bin}/khuluma --help")
    canonical = JSON.parse(shell_output("#{bin}/khuluma version --json"))
    assert_equal version.to_s, canonical.fetch("cli_version")
    assert_equal "khuluma", canonical.fetch("identity").fetch("product")
    assert_equal File.realpath(libexec/"khuluma"), canonical.fetch("identity").fetch("canonical_binary")
    refute_path_exists bin/"tmux-whisper"
    refute_path_exists libexec/"tmux-whisper"
    refute_path_exists libexec/"khuluma-lib/doctor_compat.py"
    assert_path_exists libexec/"khuluma-lib/api-version"
    assert_equal "1", (libexec/"khuluma-lib/api-version").read.strip
    assert_path_exists libexec/"khuluma-lib/recovery.py"
    assert_path_exists libexec/"khuluma-lib/migration.sh"
    assert_path_exists libexec/"khuluma-lib/finder_transaction.py"
    assert_path_exists pkgshare/"integrations/finder/khuluma-transcribe.sh"
    assert_path_exists pkgshare/"tools/khuluma_identity_migration.py"
    assert_path_exists pkgshare/"docs/INTEGRATIONS.md"
    assert_path_exists pkgshare/"native/Package.resolved"
    assert_path_exists pkgshare/"native/Sources/khulumad/CLI.swift"
    assert_path_exists pkgshare/"native/Sources/KhulumaDaemonKit/ASREngine.swift"
    refute_path_exists testpath/"profile"
    refute_path_exists testpath/"data"
  end
end
