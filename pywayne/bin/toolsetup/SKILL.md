---
name: pywayne-bin-toolsetup
description: Configure common development commands and local tool environments with pywayne's toolsetup CLI. Use whenever the user mentions toolsetup, cross-platform shell shortcuts, proxy_on/proxy_off, persistent goto aliases, the Linux gpu helper, nvm/npm bootstrap, Linux Tailscale installation, or MongoDB/PyMongo setup on macOS or Linux—even if they only ask for the right command or a dry-run plan.
---

# Pywayne Bin Toolsetup

Use `toolsetup` as the source of truth for repeatable developer-machine setup. Prefer its task interface over pasting ad-hoc rc snippets or long installer command sequences because it provides platform checks, idempotent managed blocks, confirmation, and dry-run output.

## Start safely

Identify the target platform and requested task, then preview installation work first unless the user explicitly asks you to execute it:

```bash
toolsetup --task <shortcuts|npm|tailscale|mongodb|all> --platform <auto|macos|linux|windows> --dry-run
```

Use `--yes` only when the user has authorized actual installation. npm, Tailscale, and MongoDB may download software and use `sudo`; shortcut-only configuration does not require the confirmation flag.

An explicit platform that differs from the host is accepted only with `--dry-run`. Do not work around that guard.

## Support matrix

| Task | macOS | Linux | Windows |
|---|---|---|---|
| `shortcuts` | bash/zsh | bash/zsh, including `gpu` | PowerShell |
| `npm` | yes | yes | no |
| `tailscale` | no | yes | no |
| `mongodb` | yes | yes | no |

`--task all` selects only tasks supported by the target platform. On Windows this means `shortcuts` only. Do not claim that the `gpu` command is available on macOS or Windows; by design it is Linux-only.

## Shortcut configuration

Use the detected shell, or select it explicitly:

```bash
toolsetup --task shortcuts --platform macos --shell zsh
toolsetup --task shortcuts --platform linux --shell bash
toolsetup.cmd --task shortcuts --platform windows
```

The Unix block provides:

- `proxy_on` / `proxy_off`: toggle HTTP, HTTPS, SOCKS, and NO_PROXY variables and Git global proxy settings.
- `goto`: persist directory shortcuts in `~/.goto_paths`.
- `gpu`: on Linux only, show NVIDIA hardware, compute processes, and VRAM totals by user.

PowerShell provides `proxy_on`, `proxy_off`, and `goto`, storing paths in `~/.goto_paths.json`.

Customize defaults and seed paths with:

```bash
toolsetup --task shortcuts --platform auto \
  --http-proxy http://127.0.0.1:7890 \
  --socks-proxy socks5://127.0.0.1:7890 \
  --no-proxy 'localhost,127.0.0.1,.example.com' \
  --goto code="$HOME/Documents/work/code" \
  --goto tools="$HOME/Documents/tools"
```

The shortcut block is enclosed by `pywayne toolsetup shortcuts` markers. If it already exists, the tool skips it. Use `--force` only when the user asks to refresh the managed block; replacement creates a timestamped rc-file backup.

After configuration, reload Unix with the exact `source <profile>` command printed by the tool. Reload PowerShell with:

```powershell
. $PROFILE
```

Common `goto` commands are `goto add <key> <path>`, `goto list`, `goto <key>`, `goto remove <key>`, and `goto clear`.

## Node.js and npm

```bash
toolsetup --task npm --platform linux --dry-run
toolsetup --task npm --platform linux --yes
toolsetup --task npm --platform macos --node-version 24 --yes
```

Defaults are nvm `v0.40.6`, Node.js `20`, and `https://registry.npmmirror.com`. Override them with `--nvm-version`, `--node-version`, and `--npm-registry`.

Linux installs prerequisites through apt, dnf, yum, zypper, or apk. macOS requires Xcode Command Line Tools. nvm is installed with its official installer rather than Homebrew, then the task lists LTS versions, installs the selected Node version, sets the default alias, and saves the npm registry.

## Tailscale on Linux

```bash
toolsetup --task tailscale --platform linux --dry-run
toolsetup --task tailscale --platform linux --yes
```

The task runs the official Linux installer, enables `tailscaled` when systemd is active, and runs `sudo tailscale up`. Explain that first use normally prints an authentication URL. Do not suggest this task for macOS or Windows; those platforms are intentionally outside its scope.

## MongoDB and PyMongo

```bash
toolsetup --task mongodb --platform macos --dry-run
toolsetup --task mongodb --platform macos --yes
toolsetup --task mongodb --platform linux --yes
```

The verified server line is MongoDB 8.0:

- macOS uses the official `mongodb/brew` tap and starts `mongodb-community@8.0` with `brew services`.
- Ubuntu 20.04/22.04/24.04 and Debian 12 use the official apt repository.
- RHEL-compatible distributions 8/9 use the official yum/dnf repository.
- Linux enables and starts `mongod` with systemd.

PyMongo is installed into `~/.venvs/pywayne-mongodb` by default. Use `--pymongo-venv <path>` to change it or `--skip-pymongo` to install only the server. The tool deliberately stops when the distro-provided Debian/Ubuntu `mongodb` package conflicts with `mongodb-org`; never remove that package or its data without explicit user direction.

## Verification

Use checks appropriate to the completed task:

```bash
node -v
npm -v
npm config get registry
tailscale status
systemctl status mongod
brew services list
~/.venvs/pywayne-mongodb/bin/python -c "import pymongo; print(pymongo.version)"
```

For MongoDB exposed beyond localhost, remind the user that authentication, TLS, firewall rules, and backups are separate production concerns.

## Modifying the tool

When the user asks to change implementation rather than use it, inspect these files:

- `bin/toolsetup.py`: CLI, templates, and task implementations.
- `bin/toolsetup`, `bin/toolsetup.cmd`: POSIX and Windows launchers.
- `docs/source/bin/toolsetup.rst`: user documentation.
- `setup.py` and `docs/source/index.rst`: packaging and documentation registration.

After editing, run:

```bash
python3 -m py_compile bin/toolsetup.py
git diff --check
cd docs && make html SPHINXOPTS=-W
```

Do not run actual installers as a test. Validate installation paths with `--dry-run` for Linux, macOS, and Windows.
