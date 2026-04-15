# z-edit Agent Documentation

This document outlines the structure and components of the `zedit` project for agent-based development and maintenance.

## Project Overview

**z-edit** (`zedit`) is a smart file editor launcher that automatically opens files in the appropriate editor based on MIME type or file extension. The application is intentionally designed as a single Python module for easy deployment and configuration.

### Key Characteristics

- **Single-file architecture:** `zedit.py` (1725 lines) contains the entire application
- **Zero hard dependencies:** Works with Python 3.11+ stdlib alone
- **Optional MIME detection:** `python-magic` for accurate content-based type detection
- **Layered configuration:** System-wide → user-global → project-local → ad-hoc overrides
- **AI-assisted development:** Built with Claude Sonnet 4.6 via GitHub Copilot

---

## Architecture Components

### 1. Configuration Subsystem

**Location:** `zedit.py:lines ~100-400` (approx)

**Responsibilities:**
- Parse TOML configuration files from multiple locations
- Implement deep-merge algorithm for configuration layers
- Resolve configuration paths based on environment variables

**Key Functions:**
- `_parse_toml_str()` - Parse TOML from string
- `_parse_toml_file()` - Parse TOML from file
- `_deep_merge()` - Recursively merge configuration dictionaries
- `load_config()` - Load and merge config from all priority locations

**Configuration Locations (Priority Order):**
1. Built-in defaults
2. `/opt/etc/zedit/config.toml` (system-wide, configurable via `$ZEDIT_SYSCONFDIR`)
3. `~/.config/zedit/config.toml` (user-global)
4. `./.zedit.toml` (project-local, CWD)
5. `--config FILE` (ad-hoc override via CLI)

### 2. MIME-Type Detection Subsystem

**Location:** `zedit.py:lines ~400-500` (approx)

**Responsibilities:**
- Detect file MIME types using available methods
- Prefer `libmagic` (via `python-magic`) when available
- Fall back to extension-based guessing via `mimetypes` stdlib

**Key Functions:**
- `detect_mime()` - Detect MIME type for a file

**Detection Strategy:**
1. If `python-magic` installed: use `magic.from_file()` for content-based detection
2. Fallback: use `mimetypes.guess_type()` for extension-based detection

### 3. Editor Resolution Subsystem

**Location:** `zedit.py:lines ~500-700` (approx)

**Responsibilities:**
- Map MIME types and file extensions to editor commands
- Handle the `$EDITOR` sentinel for environment variable resolution
- Implement priority-based resolution algorithm

**Key Functions:**
- `resolve_editor()` - Resolve the editor command for a file
- `_resolve_sentinel()` - Resolve `$EDITOR` to actual command

**Resolution Algorithm:**
1. Check MIME-type mapping (if `prefer_mime=true` or no extension match)
2. Check extension mapping
3. Check base MIME-type wildcard (e.g., `image/*`)
4. Fall back to `$EDITOR` or configured default editor

### 4. CLI Subsystem

**Location:** `zedit.py:lines ~700-1725` (approx)

**Responsibilities:**
- Parse command-line arguments
- Orchestrate file processing
- Implement interactive modes and output formatting
- Group files by editor for batch execution

**Key Functions:**
- `build_parser()` - Create argument parser
- `main()` - Main entry point and control flow
- `write_default_config()` - Generate starter config template
- `print_mappings()` - Display configured mappings

**CLI Modes:**
- **Normal:** `zedit FILE` - Open file in appropriate editor
- **Dry-run:** `zedit --dry-run FILE` - Preview without launching
- **List mappings:** `zedit --list` - Show all configured editor mappings
- **Interactive choose:** `zedit --choose FILE` - Present menu of editors
- **Dump editors:** `zedit --dump FILE` - Show priority-ordered editor list
- **Interactive mapping:** `zedit --map FILE` - Update MIME/extension → editor mapping
- **Init config:** `zedit --init-config` - Create starter user config
- **Install alias:** `zedit --install-alias` - Create `ze` symlink

### 5. Helper Utilities

**Responsibilities:**
- Generate default configuration templates
- Format and display mappings
- Support interactive configuration updates

**Key Functions:**
- `write_default_config()` - Scaffold `~/.config/zedit/config.toml`
- `print_mappings()` - Display all configured editor mappings

---

## Data Structures

### ConfigLayer
```python
ConfigLayer = tuple[dict[str, Any], str]
# (parsed config dict, human-readable source label)
```

### Configuration Schema
```toml
[defaults]
editor      = "vi"         # Fallback editor
prefer_mime = true          # MIME wins over extension when both match

[mime_types]
"text/x-python"   = "vim"
"application/pdf" = "evince"
"image"           = "gimp"   # Base-type wildcard

[extensions]
".md"  = "typora"
".mp4" = "vlc"
```

---

## Development Tasks

### Code Organization Tips

1. **Single-file strategy:** All development is in `zedit.py`. Changes are localized.
2. **Section markers:** Code is divided by comment separators—respect these boundaries.
3. **Type hints:** Code uses Python 3.11+ type hints; maintain this throughout.

### Testing Areas

- **Config loading:** Test merge behavior with overlapping configurations
- **MIME detection:** Verify fallback when `python-magic` unavailable
- **Editor resolution:** Test priority ordering and sentinel resolution
- **Multi-file batching:** Ensure files are grouped correctly by editor
- **Interactive modes:** Verify `--choose`, `--dump`, and `--map` functionality

### Common Maintenance Tasks

| Task | Approach |
|---|---|
| Add new CLI flag | Modify `build_parser()` and `main()` control flow |
| Change config schema | Update `_DEFAULT_CONFIG_TOML` and config loading logic |
| Add MIME detection method | Extend `detect_mime()` with new detection strategy |
| Modify resolution priority | Update resolution algorithm in `resolve_editor()` |
| Add configuration location | Extend config path resolution in `load_config()` |

---

## Configuration Defaults

The `_DEFAULT_CONFIG_TOML` constant defines built-in defaults that are always loaded first. These provide a reasonable baseline for common file types and editors.

Key defaults typically include:
- Text editors for source code (vim, nano, emacs)
- Document viewers (evince for PDF, feh for images)
- Media players (vlc for video)
- Extension-based overrides for special formats

---

## Dependencies

| Dependency | Required | Purpose |
|---|---|---|
| Python | >= 3.11 | `tomllib` in stdlib |
| `python-magic` | Optional | Content-based MIME detection via libmagic |
| `tomli` | Conditional | Backport for Python < 3.11 (if needed) |

---

## Entry Points

The project defines two entry points in `pyproject.toml`:
- `zedit` - Main command
- `ze` - Alias for `zedit`

Both point to the `main()` function in `zedit.py`.

---

## Build and Packaging

Build documentation is available in `docs/build.md`. The project supports multiple build paths:
- pip/wheel (editable: `pip install -e .`)
- CMake (for system-wide installation)
- CPack (DEB/RPM/TGZ packages)
- dpkg-buildpackage (Debian native builds)

---

## Documentation Files

| File | Purpose |
|---|---|
| `docs/user-guide.md` | Installation, CLI reference, configuration format, examples, troubleshooting |
| `docs/design.md` | Architecture, module internals, public API, data-flow, design decisions |
| `docs/build.md` | All build paths, packaging instructions, release checklist |
| `docs/cicd-guide.md` | CI/CD pipeline configuration |
| `README.md` | Quick start and overview |

---

## Version Information

- **Current Version:** 0.1.0
- **Python Requirement:** >= 3.11
- **License:** MIT
