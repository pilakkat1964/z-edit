---
layout: default
title: Z-Edit Documentation
---

# Z-Edit — Smart File Editor Launcher

**Automatically open files in the right editor based on MIME type or file extension.**

A single-file Python application that intelligently launches appropriate editors for any file type through layered TOML configuration.

## Quick Links

- **[GitHub Repository](https://github.com/pilakkat1964/z-edit)** - Source code and issue tracking
- **[Latest Release](https://github.com/pilakkat1964/z-edit/releases)** - Download latest version

---

## 🚀 Quick Start

### Check & Setup Environment

```bash
# Check dependencies only
./setup-env.sh

# Setup with prompts
./setup-env.sh --install

# Setup automatically
./setup-env.sh --force
```

### Activate & Use

```bash
# Activate virtual environment
source .venv/bin/activate

# Use zedit
zedit myfile.py              # Open with configured editor
ze document.pdf              # Use 'ze' alias
zedit --list                 # Show all configured mappings
zedit --dry-run *.md         # Preview without opening
zedit --init-config          # Create user config
```

---

## 📚 Documentation

### Getting Started
- **[Installation Guide](user-guide.md#installation)** - Multiple installation methods
- **[Quick Reference](user-guide.md#quick-reference)** - Common commands and flags
- **[Configuration Guide](user-guide.md#configuration)** - Setup TOML files

### For Users
- **[User Guide](user-guide.md)** - Complete usage documentation
  - Installation (pip, uv, system packages)
  - CLI reference with all flags and options
  - Configuration format and examples
  - MIME type detection explained
  - Troubleshooting common issues

### For Developers & Agents
- **[Design Document](design.md)** - Architecture and internals
  - Module structure and dependency graph
  - Configuration subsystem details
  - MIME detection strategy
  - Editor resolution algorithm
  - Extension points and customization
  
- **[Agent Documentation](../AGENTS.md)** - Agent-specific guidance
  - Project organization
  - Development tasks
  - Testing guidelines
  - Common maintenance procedures

- **[Build Guide](build.md)** - Build and packaging
  - Multiple build paths (pip, wheel, CMake, system packages)
  - Packaging for different distributions
  - Release checklist
  - CI/CD pipeline setup

- **[GitHub Actions CI/CD](github-actions.md)** - Automation workflows
  - Continuous Integration (testing, linting)
  - Automated Release (multi-platform packaging)
  - Source and Debian packages (amd64, arm64)
  - Security scanning

---

## 💡 Use Cases

### Web Developer
Switch between multiple terminal environments for frontend, backend, and DevOps tasks:

```bash
zedit main.py         → vim (text/x-python)
zedit styles.css      → neovim (text/css)
zedit report.pdf      → evince (application/pdf)
zedit image.png       → gimp (image/png)
```

### System Administrator
Configure editors for different file types and access them consistently across systems

### DevOps Engineer
Set up project-specific editor mappings in `.zedit.toml` for team consistency

---

## 🎯 Key Features

✓ **Single-file application** - Easy deployment, no complex dependencies  
✓ **Zero hard dependencies** - Works with Python 3.11+ stdlib  
✓ **Layered configuration** - System-wide, user-global, and project-local  
✓ **MIME type detection** - Content-based (libmagic) or extension-based fallback  
✓ **Interactive modes** - Choose editor, preview, or dump editor list  
✓ **Environment integration** - Respects `$EDITOR`, `$VISUAL` variables  
✓ **Fast setup** - Automated environment checker with `setup-env.sh`

---

## 🛠️ Build & Dependency Management

This project uses **uv** for fast, reproducible builds:

### Quick Setup Commands

```bash
# Check environment (dry-run)
./setup-env.sh

# Setup interactively with prompts
./setup-env.sh --install

# Auto-install everything
./setup-env.sh --force

# Show all options
./setup-env.sh --help
```

The `setup-env.sh` script:
- Checks Python version (>= 3.11)
- Verifies uv tool installation
- Detects system dependencies (libmagic)
- Creates virtual environment with all extras
- Provides clear guidance for optional dependencies

### Traditional Installation

```bash
# Using pip
pip install .
pip install ".[magic]"   # with MIME detection support

# Using uv (faster)
uv sync
uv sync --all-extras
```

---

## 📋 Configuration

Config files (TOML format) are loaded and merged in this order:

| Priority | Location | Purpose |
|---|---|---|
| 1 | Built-in defaults | Always present |
| 2 | `/opt/etc/zedit/config.toml` | System-wide |
| 3 | `~/.config/zedit/config.toml` | User-global |
| 4 | `./.zedit.toml` in CWD | Project-local |
| 5 | `--config FILE` | Ad-hoc override |

### Example Configuration

```toml
[defaults]
editor      = "$EDITOR"   # Uses $VISUAL → $EDITOR → vi
prefer_mime = true         # MIME wins over extension

[mime_types]
"text/x-python"   = "vim"
"application/pdf" = "evince"
"image"           = "gimp"    # wildcard: all image/* types

[extensions]
".md"  = "typora"
".mp4" = "vlc"
```

---

## 🔧 System Requirements

**Required:**
- Python >= 3.11 (for `tomllib` in stdlib)

**Recommended:**
- `python-magic` (for accurate content-based MIME detection)
- `uv` >= 0.11.0 (for faster dependency management)

**Optional:**
- libmagic development files (for `python-magic` support)

---

## 📞 Support & Issues

Found a bug or have a feature request?

- **[Open an Issue](https://github.com/pilakkat1964/z-edit/issues)** - Report bugs or request features
- **[Discussions](https://github.com/pilakkat1964/z-edit/discussions)** - Ask questions and share ideas

---

## 📄 License

MIT License - Free for personal and commercial use

---

## 🙏 Acknowledgments

Z-edit was designed and built to explore AI-assisted development using **Claude Sonnet 4.6** via **GitHub Copilot**.

**Explore the code:** This is an excellent resource for learning Python patterns:
- Layered configuration systems
- MIME type detection strategies
- CLI design with argparse
- TOML parsing and merging
- Error handling and validation

---

## 📱 Quick Navigation

- [Go to GitHub Repository](https://github.com/pilakkat1964/z-edit)
- [View Full User Guide](user-guide.md)
- [Read Architecture Design](design.md)
- [Check Build Options](build.md)
- [See Agent Documentation](../AGENTS.md)

---

**Ready to simplify your file editing workflow?** Start with `./setup-env.sh` or jump straight to the [Installation Guide](user-guide.md#installation)!
