#!/usr/bin/env python3
"""Finite public GitHub-hosted macOS release QA. Never run on a daily Mac.

No model/warmup/daemon/app/Keychain operation or manual permanent cleanup.
Normal Homebrew migrate/upgrade is confined to the disposable runner; cleanup
is disabled and old keg/profile fixtures are retained. No uninstall is run.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.parse
import urllib.request

TAP = 'ricardo-nth/tap'
SOURCE_REPO = 'https://github.com/ricardo-nth/khuluma.git'
LEGACY_COMMIT = 'd0152e45f84551b71a679cfc32da0b9821d8f4f9'
LEGACY_URL = 'https://github.com/ricardo-nth/khuluma/archive/refs/tags/v0.9.0.tar.gz'
FIXTURE_SHA = '3b609395f1b31ec8c029116aa8708e3f5f52d463311964aa2a7cf3406662ba60'
HERE = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise RuntimeError(message)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def private_dir(path):
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    require(path.is_dir() and not path.is_symlink() and path.stat().st_uid == os.getuid(), 'unsafe private fixture directory')
    return path


def put(path, data, mode=0o600):
    private_dir(path.parent)
    with path.open('xb') as handle:
        handle.write(data.encode() if isinstance(data, str) else data)
    path.chmod(mode)


def snapshot(paths):
    result = {}
    for root in paths:
        if not root.exists() and not root.is_symlink():
            result[str(root)] = None
            continue
        for path in [root, *sorted(root.rglob('*'))] if root.is_dir() else [root]:
            info = path.lstat()
            require(not stat.S_ISLNK(info.st_mode), 'profile fixture contains a symlink')
            require(stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode), 'profile contains a runtime endpoint')
            result[str(path)] = [stat.S_IFMT(info.st_mode), stat.S_IMODE(info.st_mode), info.st_mtime_ns,
                                 sha(path) if path.is_file() else None]
    return result


def command(args, env, expect=0):
    print('+ ' + ' '.join(map(str, args)), flush=True)
    result = subprocess.run(list(map(str, args)), env=env, capture_output=True, text=True, timeout=1200)
    require(result.returncode == expect, 'command returned ' + str(result.returncode) + ': ' + result.stderr[-3000:])
    return result.stdout


def formula_fields(path):
    text = path.read_text()
    url = re.findall(r'^  url "([^"]+)"$', text, re.M)
    checksum = re.findall(r'^  sha256 "([0-9a-f]{64})"$', text, re.M)
    require(len(url) == len(checksum) == 1, 'candidate must contain one actual final-tag URL and measured SHA256')
    match = re.fullmatch(r'https://github.com/ricardo-nth/khuluma/archive/refs/tags/v(\d+\.\d+\.\d+)\.tar\.gz', url[0])
    require(match and match.group(1) != '0.9.0', 'canonical source must be the actual final canonical tag')
    require('class Khuluma < Formula' in text and '@KHULUMA_' not in text, 'candidate is still an unresolved template')
    install = re.search(r'^  def install\n(.*?)^  end$', text, re.M | re.S)
    require(install is not None, 'candidate install body missing')
    code = '\n'.join(line.split('#', 1)[0] for line in install.group(1).splitlines())
    require(not re.search(r'\b(system|exec|spawn|download)\b|warmup|swift build', code)
            and 'def post_install' not in text and 'service do' not in text,
            'this source-only QA refuses install hooks that could build, warm or start runtime')
    return {'url': url[0], 'sha256': checksum[0], 'version': match.group(1)}


def validate_inputs(args):
    candidate = Path(args.candidate).resolve()
    require(candidate.is_file() and candidate.is_relative_to(HERE.parent), 'candidate must be inside this tap checkout')
    legacy = HERE / 'fixtures/tmux-whisper-v0.9.0.rb'
    require(sha(legacy) == FIXTURE_SHA, 'preserved v0.9.0 formula fixture changed')
    require(re.fullmatch('[0-9a-f]{64}', args.legacy_sha256), 'actual renamed v0.9 archive checksum is required')
    require(re.fullmatch('[0-9a-f]{40}', args.canonical_commit), 'actual final tag commit is required')
    require(json.loads((HERE / 'formula_renames.json').read_text()) == {'tmux-whisper': 'khuluma'}, 'unexpected rename map')
    return candidate, legacy, formula_fields(candidate)


def verify_tag(tag, expected, env):
    output = command(['git', 'ls-remote', SOURCE_REPO, 'refs/tags/' + tag, 'refs/tags/' + tag + '^{}'], env)
    rows = dict(reversed(line.split()) for line in output.splitlines() if line.strip())
    actual = rows.get('refs/tags/' + tag + '^{}', rows.get('refs/tags/' + tag))
    require(actual == expected, 'source tag no longer resolves to the reviewed immutable commit: ' + tag)


def archive(url, expected, target, required, version_marker):
    # The fixed GitHub HTTPS endpoint may redirect only to its codeload host.
    with urllib.request.urlopen(url, timeout=60) as response:
        require(urllib.parse.urlparse(response.url).hostname in ('github.com', 'codeload.github.com'), 'unexpected archive redirect')
        with target.open('xb') as handle:
            shutil.copyfileobj(response, handle)
    target.chmod(0o600)
    require(sha(target) == expected, 'actual archive bytes do not match reviewed checksum')
    with tarfile.open(target, 'r:gz') as archive_file:
        members = archive_file.getmembers()
        roots = set()
        payload = {}
        for member in members:
            path = PurePosixPath(member.name)
            require(not path.is_absolute() and '..' not in path.parts and path.parts,
                    'unsafe source archive member')
            require(member.isdir() or member.isfile(), 'unexpected archive link or special file')
            roots.add(path.parts[0])
            if len(path.parts) > 1:
                payload[str(PurePosixPath(*path.parts[1:]))] = member
        require(len(roots) == 1 and all(name in payload for name in required), 'archive root or required payload differs')
        source = archive_file.extractfile(payload[version_marker[0]]).read()
        require(version_marker[1].encode() in source, 'archive CLI version is not the expected unchanged tag')
    return {'url': url, 'sha256': expected, 'root': next(iter(roots)), 'files': len(payload)}


def git_commit(repo, message, env):
    command(['git', '-C', repo, '-c', 'user.name=Khuluma QA', '-c', 'user.email=qa@example.invalid', 'add', '--all'], env)
    command(['git', '-C', repo, '-c', 'user.name=Khuluma QA', '-c', 'user.email=qa@example.invalid', 'commit', '-m', message], env)


def product_roots(home):
    return [home/'.config/dictate', home/'.config/khuluma', home/'.local/share/tmux-whisper',
            home/'.local/share/khuluma', home/'.local/share/sounds/dictate', home/'.local/share/sounds/khuluma']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario', choices=('fresh', 'upgrade'), required=True)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--canonical-commit', required=True)
    parser.add_argument('--legacy-sha256', required=True)
    parser.add_argument('--check-only', action='store_true', help='static validation only; no brew, network, profile or tap mutation')
    args = parser.parse_args()
    candidate, legacy, final = validate_inputs(args)
    if args.check_only:
        print(json.dumps({'state':'static-inputs-valid', 'version':final['version'], 'scenario':args.scenario}))
        return
    require(sys.platform == 'darwin' and os.environ.get('GITHUB_ACTIONS') == 'true'
            and os.environ.get('RUNNER_OS') == 'macOS' and os.environ.get('RUNNER_ENVIRONMENT') == 'github-hosted'
            and os.environ.get('QA_PUBLIC_STANDARD_RUNNER') == '1', 'only the candidate public standard GitHub-hosted macOS workflow may execute QA')
    require(os.environ.get('GITHUB_REPOSITORY') == 'ricardo-nth/homebrew-tap', 'unexpected repository; no daily Mac or other repository run')
    runner_temp = Path(os.environ['RUNNER_TEMP']).resolve()
    require(runner_temp.is_dir() and runner_temp.stat().st_uid == os.getuid(), 'runner temporary directory is not owned')
    qa_root = Path(tempfile.mkdtemp(prefix='khuluma-brew-qa-', dir=runner_temp))
    qa_root.chmod(0o700)
    qa_home = private_dir(qa_root/'home')
    # Child HOME means an actual synthetic home, never repurposes the invoking
    # process's HOME variable or inspects user profile contents.
    env = {k:v for k,v in os.environ.items() if not k.startswith(('KHULUMA_', 'DICTATE_', 'TMUX_WHISPER_', 'XDG_')) and k != 'SOUNDS_DIR'}
    env.update(HOME=str(qa_home), TMPDIR=str(private_dir(qa_root/'tmp')), HOMEBREW_CACHE=str(private_dir(qa_root/'cache')),
               HOMEBREW_LOGS=str(private_dir(qa_root/'logs')), HOMEBREW_NO_AUTO_UPDATE='1', HOMEBREW_NO_INSTALL_CLEANUP='1',
               HOMEBREW_NO_CLEANUP_FORMULAE='tmux-whisper,khuluma,ffmpeg,python@3.15', HOMEBREW_NO_ANALYTICS='1',
               HOMEBREW_NO_ENV_HINTS='1', HOMEBREW_NO_ASK='1')
    env.update(DICTATE_TMPDIR=str(qa_root/'tmp'), KHULUMA_TMPDIR=str(qa_root/'tmp'),
               DICTATE_PROCESSING_DIR=str(qa_root/'processing-old'), KHULUMA_PROCESSING_DIR=str(qa_root/'processing-new'))
    original_home_roots = product_roots(Path(os.environ['HOME']))
    require(all(not p.exists() and not p.is_symlink() for p in original_home_roots), 'runner already has a product profile; refuse instead of touching it')
    original_home_snapshot = snapshot(original_home_roots)
    prefix = Path(command(['brew','--prefix'], env).strip())
    cellar = Path(command(['brew','--cellar'], env).strip())
    require(not (cellar/'tmux-whisper').exists() and not (cellar/'khuluma').exists(), 'runner already owns a product keg')
    require(TAP not in command(['brew','tap'], env).splitlines(), 'runner already has the tap')
    brew_version = command(['brew','--version'], env).splitlines()[0]
    verify_tag('v0.9.0', LEGACY_COMMIT, env)
    verify_tag('v'+final['version'], args.canonical_commit, env)
    legacy_archive = archive(LEGACY_URL, args.legacy_sha256, qa_root/'legacy.tar.gz',
                             ['bin/tmux-whisper','bin/dictate-lib.sh','tmux-whisperd/Package.resolved'],
                             ('bin/tmux-whisper','TMUX_WHISPER_CLI_VERSION="0.9.0"'))
    canonical_archive = archive(final['url'], final['sha256'], qa_root/'canonical.tar.gz',
        ['bin/khuluma','bin/tmux-whisper','bin/khuluma-lib.sh','bin/khuluma-lib/api-version',
         'bin/khuluma-lib/identity.sh','bin/khuluma-lib/migration.sh','bin/khuluma-lib/recovery.py',
         'native/Package.resolved','native/Sources/khulumad/CLI.swift',
         'native/Sources/KhulumaDaemonKit/ASREngine.swift','integrations/finder/khuluma-transcribe.sh',
         'tools/khuluma_identity_migration.py'], ('bin/khuluma','KHULUMA_CLI_VERSION="'+final['version']+'"'))
    # Dependencies must be bottles; this QA never compiles ASR/app products.
    command(['brew','install','--force-bottle','--keep-tmp','ffmpeg','python@3.15'], env)
    fixture_tap = private_dir(qa_root/'tap-origin')
    private_dir(fixture_tap/'Formula')
    command(['git','init','-b','main',fixture_tap], env)
    legacy_text = legacy.read_text()
    overridden, count_url = re.subn(r'^  url "[^"]+"$', '  url "'+LEGACY_URL+'"', legacy_text, count=1, flags=re.M)
    overridden, count_sha = re.subn(r'^  sha256 "[^"]+"$', '  sha256 "'+args.legacy_sha256+'"', overridden, count=1, flags=re.M)
    require(count_url == count_sha == 1, 'legacy transport-only fixture override failed')
    put(qa_root/'legacy-transport-override.rb', overridden)
    if args.scenario == 'upgrade':
        put(fixture_tap/'Formula/tmux-whisper.rb', overridden)
    else:
        shutil.copy2(candidate, fixture_tap/'Formula/khuluma.rb')
        shutil.copy2(HERE/'formula_renames.json', fixture_tap/'formula_renames.json')
    git_commit(fixture_tap, 'QA initial tap state', env)
    command(['brew','tap',TAP,fixture_tap.as_uri()], env)
    installed_tap = Path(command(['brew','--repo',TAP], env).strip())
    require(installed_tap.is_relative_to(Path(command(['brew','--repository'], env).strip())/'Library/Taps'), 'unexpected tap checkout path')
    legacy_profile = qa_home/'.config/dictate'
    old_keg_backup = None
    if args.scenario == 'upgrade':
        command(['brew','install','--formula','--keep-tmp',TAP+'/tmux-whisper'], env)
        old_keg = Path(command(['brew','--prefix',TAP+'/tmux-whisper'], env).strip()).resolve()
        require(old_keg.name == '0.9.0', 'initial installed package is not genuine v0.9.0')
        require(json.loads((old_keg/'INSTALL_RECEIPT.json').read_text())['source']['tap'] == TAP, 'legacy keg receipt belongs to a different tap')
        require('0.9.0' in command([prefix/'bin/tmux-whisper','--version'], env), 'old executable does not report v0.9.0')
        if legacy_profile.exists():
            legacy_profile.rename(qa_root/'retained-old-probe-profile')
        old_keg_backup = qa_root/'retained-v0.9.0-keg'
        shutil.copytree(old_keg, old_keg_backup, symlinks=True)
    else:
        empty_home = snapshot(product_roots(qa_home))
        command(['brew','install','--formula','--keep-tmp',TAP+'/khuluma'], env)
        fresh = json.loads(command([prefix/'bin/khuluma','version','--json'], env))
        require(fresh['identity']['migration_required'] is False and fresh['identity']['config_dir'] == str(qa_home/'.config/khuluma'), 'fresh default identity/root differs')
        command([prefix/'bin/khuluma','--help'], env)
        command([prefix/'bin/khuluma','config','defaults'], env)
        require(snapshot(product_roots(qa_home)) == empty_home, 'fresh installation or pure probes created a user profile/data tree')
    # Deliberately synthetic old profile; installation/upgrade and read-only
    # canonical probes must preserve its bytes, mode and mtime exactly.
    put(legacy_profile/'config.toml', '[meta]\nconfig_version=1\n[swift_parakeet]\nmodel_path=""\nsocket_path=""\n')
    put(legacy_profile/'vocab', 'synthetic → retained\n')
    put(legacy_profile/'usage.json', json.dumps({'schema_version':1,'delivered_dictations':{'count':9,'by_flow':{'inline':9,'tmux':0}},
        'processed_words':72,'recording_duration_ms':9000,'full_elapsed_duration_ms':11000}))
    baseline = snapshot(product_roots(qa_home))
    if args.scenario == 'upgrade':
        require(not (cellar/'khuluma').exists(), 'canonical rack must be absent before genuine migration; conflict-merging is not allowed')
        (installed_tap/'Formula/tmux-whisper.rb').rename(qa_root/'retained-old-tap-formula.rb')
        shutil.copy2(candidate, installed_tap/'Formula/khuluma.rb')
        shutil.copy2(HERE/'formula_renames.json', installed_tap/'formula_renames.json')
        git_commit(installed_tap, 'khuluma: renamed from tmux-whisper (QA)', env)
        require(not command(['git','-C',installed_tap,'status','--porcelain'], env).strip(), 'fixture tap transition is not fully committed')
        # Trust only our verified canonical fixture formula. Homebrew trust
        # intentionally does not follow the old formula name during a rename.
        command(['brew','trust','--formula',TAP+'/khuluma'], env)
        command(['brew','migrate','--dry-run',TAP+'/tmux-whisper'], env)
        command(['brew','migrate',TAP+'/tmux-whisper'], env)
        require((cellar/'tmux-whisper').is_symlink() and (cellar/'tmux-whisper').resolve() == (cellar/'khuluma').resolve(), 'old rack was not migrated to canonical ownership')
        require((cellar/'khuluma/0.9.0').is_dir(), 'migrate did not retain the genuine old installed payload')
        require(json.loads((cellar/'khuluma/0.9.0/INSTALL_RECEIPT.json').read_text())['source']['tap'] == TAP, 'migrated old receipt lost same-tap identity')
        require('0.9.0' in command(['brew','list','--versions',TAP+'/khuluma'], env), 'migration alone lost old installed version')
        command(['brew','upgrade','--formula','--keep-tmp',TAP+'/khuluma'], env)
    require(snapshot(product_roots(qa_home)) == baseline, 'Brew installation/upgrade changed a synthetic user profile')
    new_keg = (prefix/'opt/khuluma').resolve()
    require(new_keg.name == final['version'] and new_keg.parent == cellar/'khuluma', 'canonical opt does not select final version')
    require(json.loads((new_keg/'INSTALL_RECEIPT.json').read_text())['source']['tap'] == TAP, 'canonical keg receipt belongs to a different tap')
    for name in ('khuluma','tmux-whisper','khuluma-lib.sh'):
        require((prefix/'bin'/name).is_symlink() and (prefix/'bin'/name).resolve().is_relative_to(new_keg), 'public command/library has a different owner: '+name)
    if args.scenario == 'upgrade':
        require((prefix/'opt/tmux-whisper').resolve() == new_keg, 'old opt route does not resolve to the canonical current keg')
        require((cellar/'khuluma/0.9.0').is_dir() and old_keg_backup.is_dir(), 'automatic cleanup removed recovery payload')
        require(sha(cellar/'khuluma/0.9.0/libexec/tmux-whisper') == sha(old_keg_backup/'libexec/tmux-whisper'), 'migration changed retained old CLI code')
        require(not (prefix/'bin/dictate-lib.sh').exists() and not (prefix/'bin/dictate-lib.sh').is_symlink(), 'old library remains an active public link')
    version = json.loads(command([prefix/'bin/khuluma','version','--json'], env))
    compatibility = json.loads(command([prefix/'bin/tmux-whisper','version','--json'], env))
    require(version == compatibility and version['schema_version'] == 1 and version['cli_version'] == final['version'], 'canonical and shim wrappers/schema differ')
    require(version['identity']['product'] == 'khuluma' and version['identity']['identity_version'] == 1
            and version['identity']['canonical_binary'] == str(new_keg/'libexec/khuluma')
            and version['running_binary']['path'] == version['identity']['canonical_binary']
            and version['identity']['migration_required'] is True, 'wrapper identity or legacy admission refusal differs')
    require(snapshot(product_roots(qa_home)) == baseline, 'pure version probes changed the legacy profile')
    result = subprocess.run([str(prefix/'bin/khuluma'),'app-config','--json'], env=env, capture_output=True, text=True)
    require(result.returncode == 2 and not (qa_home/'.config/khuluma').exists(), 'new CLI did not refuse un-migrated default profile')
    require(snapshot(product_roots(qa_home)) == baseline, 'refusal changed existing legacy data')
    share = new_keg/'share/khuluma'
    for name in ('native/Package.swift','native/Package.resolved','native/Sources/khulumad/CLI.swift',
                 'native/Sources/KhulumaDaemonKit/ASREngine.swift','tools/khuluma_identity_migration.py',
                 'integrations/finder/khuluma-transcribe.sh','config/config.toml','assets/sounds/khuluma/start.wav'):
        require((share/name).is_file(), 'missing installed payload: '+name)
    require((new_keg/'libexec/khuluma-lib/api-version').read_text().strip() == '1', 'shell library API marker differs')
    require((share/'native/Tests').is_dir(), 'native package test target directory missing')
    require(not (share/'native/.build').exists(), 'formula shipped or built native artifacts unexpectedly')
    # Dedicated synthetic contract profile, retained for inspection; never the
    # legacy fixture or runner user's profile.
    profile = qa_root/'contract-profile'
    put(profile/'config.toml', (share/'config/config.toml').read_bytes())
    contract_env = dict(env, KHULUMA_CONFIG_DIR=str(profile), XDG_DATA_HOME=str(qa_root/'contract-data'))
    config = json.loads(command([prefix/'bin/khuluma','app-config','--json'], contract_env))
    require(config['schema_version'] == 1 and config['app_contract'] == 3 and config['cleanup']['config_dir'] == str(profile)
            and config['transcription']['socket_path'] == str(profile/'.cache/khulumad.sock'), 'app contract/default canonical root differs')
    pure_before = snapshot([profile, qa_root/'contract-data'])
    command([prefix/'bin/khuluma','--help'], contract_env)
    command([prefix/'bin/khuluma','config','defaults'], contract_env)
    doctor = json.loads(command([prefix/'bin/khuluma','doctor','--json'], contract_env))
    old_doctor = json.loads(command([prefix/'bin/tmux-whisper','doctor','--json'], contract_env))
    require(doctor['schema_version'] == 2, 'doctor schema differs')
    reported_source = Path(doctor['install_sanity']['daemon_source']['path'])
    expected_source = share/'native'
    print(json.dumps({'doctor_source_reported':str(reported_source), 'doctor_source_expected':str(expected_source)}), flush=True)
    require(reported_source.resolve(strict=True) == expected_source.resolve(strict=True)
            and (reported_source/'Package.swift').samefile(expected_source/'Package.swift'),
            'doctor source discovery does not identify this canonical keg package')
    require('cli_binary' in doctor['install_sanity'] and 'tmux_whisper_binary' in old_doctor['install_sanity']
            and 'schema_version' not in old_doctor, 'legacy doctor adapter differs')
    require(snapshot([profile, qa_root/'contract-data']) == pure_before, 'read-only probes changed contract profile/data')
    command(['brew','audit','--strict',TAP+'/khuluma'], env)
    command(['brew','test','--keep-tmp',TAP+'/khuluma'], env)
    ownership = command(['brew','list','--verbose','--formula',TAP+'/khuluma'], env).splitlines()
    require(ownership and all(Path(p).resolve().is_relative_to(cellar/'khuluma') for p in ownership), 'formula claims an external user profile or another rack owner')
    # Homebrew intentionally keeps an old-name rack symlink, and plain list
    # can show that alias. Count physical product racks, then prove opt/bin
    # ownership above; an alias is not a second package owner.
    owners = [name for name in ('khuluma','tmux-whisper') if (cellar/name).is_dir() and not (cellar/name).is_symlink()]
    require(owners == ['khuluma'], 'product has more than one formula owner')
    require(snapshot(product_roots(qa_home)) == baseline and snapshot(original_home_roots) == original_home_snapshot, 'a protected user profile changed')
    report = {'state':'passed','scenario':args.scenario,'brew':brew_version,'machine':platform.machine(),
              'canonical_archive':canonical_archive,'legacy_archive':legacy_archive,'canonical_commit':args.canonical_commit,
              'legacy_commit':LEGACY_COMMIT,'canonical_keg':str(new_keg),'retained_fixture_root':str(qa_root),
              'old_keg_snapshot':str(old_keg_backup) if old_keg_backup else None,
              'ownership_entries':len(ownership),'uninstall':'not run; ownership and unchanged-profile checks only',
              'runtime':'no model download, warmup, daemon/app build/start or Keychain operation'}
    put(qa_root/'report.json', json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary,'a') as handle:
            handle.write('Khuluma Homebrew '+args.scenario+' QA passed. Final CLI '+final['version']+'. '
                         'No uninstall or product runtime was run. Synthetic fixtures retained for this runner lifetime.\n')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('Homebrew QA refused/failed: '+str(exc), file=sys.stderr)
        raise SystemExit(1)
