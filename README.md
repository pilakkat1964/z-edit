# edit — smart file editor launcher

`edit` opens files in the right editor automatically. It detects each file's
MIME type (via **libmagic** or the `mimetypes` stdlib) and maps it to an editor
through a layered TOML configuration — system-wide, per-user, and per-project.

```
edit main.py          → vim          (text/x-python mapping)
edit report.pdf       → evince       (application/pdf mapping)
edit image.png        → gimp         (image/png mapping)
edit README.md        → typora       (.md extension mapping)
```

---

## Quick start

```bash
# Install
pip install .                   # from source
pip install ".[magic]"          # with accurate content-based MIME detection

# Use
edit myfile.py                  # open with the configured editor
ed myfile.py                    # same — 'ed' is a symlink/alias for 'edit'
edit --dry-run *.md             # preview without opening
edit --list                     # show all configured mappings
edit --init-config              # scaffold ~/.config/edit/config.toml
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
| 2 | `/etc/edit/config.toml` | System-wide (installed by OS package) |
| 3 | `~/.config/edit/config.toml` | User-global |
| 4 | `./.edit.toml` in CWD | Project-local |
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
