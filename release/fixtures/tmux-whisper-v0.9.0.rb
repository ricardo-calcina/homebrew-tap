class TmuxWhisper < Formula
  desc "Tmux-first macOS voice dictation CLI with local ASR backends"
  homepage "https://github.com/ricardo-nth/tmux-whisper"
  url "https://github.com/ricardo-nth/tmux-whisper/archive/refs/tags/v0.9.0.tar.gz"
  sha256 "3012f39513cf50516411828730b786c393ff1792b84b55c971123f8c26f00d3d"
  license "MIT"

  depends_on :macos

  def install
    libexec.install "bin/tmux-whisper", "bin/dictate-lib.sh", "bin/tmux-whisper-lib"
    (bin/"tmux-whisper").write_env_script(
      libexec/"tmux-whisper",
      DICTATE_LIB_PATH:         libexec/"dictate-lib.sh",
      DICTATE_INTERNAL_LIB_DIR: libexec/"tmux-whisper-lib",
    )
    bin.install_symlink libexec/"dictate-lib.sh" => "dictate-lib.sh"

    pkgshare.install "config", "integrations", "assets", "tools", "tmux-whisperd"
    pkgshare.install "install.sh", "bootstrap.sh", "README.md", "CHANGELOG.md"
  end

  def caveats
    <<~EOS
      Optional defaults and assets (paths remain under `dictate` for now):

        cp -Rn "#{opt_pkgshare}/config" "$HOME/.config/dictate"
        mkdir -p "$HOME/.local/share/sounds/dictate"
        cp -n "#{opt_pkgshare}/assets/sounds/dictate/"*.wav "$HOME/.local/share/sounds/dictate/" 2>/dev/null || true

      Then run:

        tmux-whisper debug
    EOS
  end

  test do
    output = shell_output("#{bin}/tmux-whisper --help")
    assert_match "tmux-whisper: local dictation for macOS", output
    assert_match "CLI version: #{version}", shell_output("#{bin}/tmux-whisper --version")
  end
end
