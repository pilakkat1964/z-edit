# zedit — smart file editor launcher

> **About this project:** `zedit` was designed and built to explore the power of
> AI-assisted development. The entire codebase was written primarily using
> **Claude Sonnet 4.6** (the "medium" model) accessed through **GitHub Copilot**.

`zedit` opens files in the right editor automatically. It detects each file's
MIME type (via **libmagic** or the `mimetypes` stdlib) and maps it to an editor
through a layered TOML configuration — system-wide, per-user, and per-project.

```
zedit main.py          → vim          (text/x-python mapping)
zedit report.pdf       → evince       (application/pdf mapping)
zedit image.png        → gimp         (image/png mapping)
zedit README.md        → typora       (.md extension mapping)
```

---

## Quick start

### Using `uv` (recommended)

```bash
# Check and set up build environment
./setup-env.sh              # Check dependencies only
./setup-env.sh --install    # Check and interactively install
./setup-env.sh --force      # Install everything without prompting

# Activate virtual environment
source .venv/bin/activate

# Use
zedit myfile.py                  # open with the configured editor
ze myfile.py                    # same — 'ze' is a symlink/alias for 'zedit'
zedit --dry-run *.md             # preview without opening
zedit --list                     # show all configured mappings
zedit --init-config              # scaffold ~/.config/zedit/config.toml
```

### Using `pip` (traditional)

```bash
# Install from source
pip install .                   # from source
pip install ".[magic]"          # with accurate content-based MIME detection

# Use
zedit myfile.py                  # open with the configured editor
ze myfile.py                    # same — 'ze' is a symlink/alias for 'zedit'
zedit --dry-run *.md             # preview without opening
zedit --list                     # show all configured mappings
zedit --init-config              # scaffold ~/.config/zedit/config.toml
```

---

## Build Environment Setup

This project includes an automated build environment setup script (`setup-env.sh`) that checks and reports on all dependencies.

### What the setup script does

- ✓ Checks Python version (requires >= 3.11)
- ✓ Verifies `uv` tool installation
- ✓ Detects system-level dependencies (libmagic)
- ✓ Creates virtual environment with all dependencies
- ✓ Installs optional extras (magic support for accurate MIME detection, dev tools)

### Setup script usage

```bash
./setup-env.sh                # Dry-run: check dependencies only
./setup-env.sh --install      # Check and prompt for installation
./setup-env.sh --force        # Check and install everything (no prompts)
./setup-env.sh --help         # Show help message
```

---

## Documentation

| Document | Contents |
|---|---|
| [docs/user-guide.md](docs/user-guide.md) | Installation, CLI reference, configuration format, MIME detection, examples, troubleshooting |
| [docs/design.md](docs/design.md) | Architecture, module internals, public API, data-flow, design decisions |
| [docs/build.md](docs/build.md) | All build paths: pip/wheel, CMake, CPack (DEB/RPM/TGZ), `dpkg-buildpackage`, release checklist |

---

## Configuration at a glance

Config files are TOML, loaded and deep-merged in this order:

| Priority | Location | Purpose |
|---|---|---|
| 1 | Built-in defaults | Always present |
| 2 | `/etc/zedit/config.toml` | System-wide (installed by OS package) |
| 3 | `~/.config/zedit/config.toml` | User-global |
| 4 | `./.zedit.toml` in CWD | Project-local |
| 5 | `--config FILE` | Ad-hoc override |

```toml
[defaults]
editor      = "$EDITOR"   # resolved via $VISUAL -> $EDITOR -> vi
prefer_mime = true         # MIME wins over extension when both match

[mime_types]
"text/x-python"   = "vim"
"application/pdf" = "evince"
"image"           = "gimp"    # base-type wildcard: all image/* types

[extensions]
".md"  = "typora"
".mp4" = "vlc"
```

---

## Dependencies

| Package | Required | Purpose |
|---|---|---|
| Python >= 3.11 | Yes | `tomllib` in stdlib |
| `python-magic` | Recommended | Content-based MIME detection via libmagic |

Without `python-magic` the app falls back to extension-based guessing.
