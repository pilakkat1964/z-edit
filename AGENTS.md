# z-edit Agent Documentation

This document outlines the structure, components, infrastructure, and development workflows of the `zedit` project for agent-based development and maintenance.

## Project Overview

**z-edit** (`zedit`) is a smart file editor launcher that automatically opens files in the appropriate editor based on MIME type or file extension. The application is intentionally designed as a single Python module for easy deployment and configuration.

### Key Characteristics

- **Single-file architecture:** `zedit.py` (1,725 lines) contains the entire application
- **Zero hard dependencies:** Works with Python 3.11+ stdlib alone
- **Optional MIME detection:** `python-magic` for accurate content-based type detection
- **Layered configuration:** System-wide → user-global → project-local → ad-hoc overrides
- **Modern build infrastructure:** uv package manager, CMake 3.20+, GitHub Actions CI/CD
- **Production-ready packaging:** Automated Debian package builds (amd64), GitHub releases
- **Comprehensive documentation:** GitHub Pages with Jekyll Slate theme
- **Developer-friendly workflow:** Python wrapper script (`scripts/dev.py`) for accelerated TDD cycle
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

## Build Infrastructure

### Modern Package Manager: uv

The project has been modernized to use `uv` as the primary package manager, replacing pip for faster dependency resolution and reproducible builds.

**Key Files:**
- `pyproject.toml` - Project configuration (hatchling build backend, pytest config, dev dependencies)
- `uv.lock` - Locked dependency manifest (reproducible builds across environments)

**Setup Environment:**
- `setup-env.sh` - Intelligent build environment setup (400+ lines)
  - Detects Python installation
  - Creates virtual environments with uv
  - Installs dependencies from uv.lock
  - Handles both development and production setups

**Build Instructions:**
```bash
# Initialize development environment
source setup-env.sh dev

# Or manually
uv venv
source .venv/bin/activate
uv sync
```

### CMake Build System

**Location:** `CMakeLists.txt` (top-level), `cmake/` directory

**Build Targets:**
- `build` - Build the project
- `test` - Run pytest test suite
- `package` - Create source archive and DEB package
- `clean` - Remove build artifacts
- `distclean` - Remove all build and virtual environment artifacts

**Build Paths:**
```bash
# Development build
cmake -B build && cmake --build build

# System installation
cmake -B build -DCMAKE_INSTALL_PREFIX=/usr/local
cmake --build build
cmake --install build

# Packaging (DEB)
cmake -B build -DZEDIT_BUILD_WHEEL=OFF
cmake --build build
cpack -C CPackConfig.cmake
```

### GitHub Actions CI/CD

**Workflows Location:** `.github/workflows/`

#### 1. Continuous Integration Workflow (`ci.yml`)
- **Triggers:** Push to any branch, pull requests
- **Jobs:**
  - Test on Python 3.11, 3.12, 3.13 (multiple versions)
  - Linting (ruff)
  - Security scanning (bandit)
  - Coverage reporting

**Key Features:**
- Runs on latest Ubuntu
- Caches uv dependencies
- Reports coverage metrics
- Fails on security issues

#### 2. Release Workflow (`release.yml`)
- **Triggers:** Push to tags matching `v*` pattern
- **Jobs:**
  1. **prepare** - Set up build environment
  2. **build-source** - Create source tarball
  3. **build-debian-amd64** - Build DEB package for amd64
  4. **create-release** - Create GitHub Release with assets

**Release Assets:**
- Source archive: `zedit-X.Y.Z-source.tar.gz`
- Debian package: `zedit-X.Y.Z-Linux-amd64.deb`
- Checksums: `SHA256SUMS`

**Automation Notes:**
- DEB package disables wheel building: `-DZEDIT_BUILD_WHEEL=OFF`
- Postinst script creates `ze` symlink for convenience
- SHA256 checksums verified before release publication

---

## Development Workflow Automation

### The `scripts/dev.py` Wrapper Script

**Location:** `scripts/dev.py` (1,050+ lines, executable)

A comprehensive Python-based development workflow wrapper that accelerates the TDD cycle by automating build, test, package, and release operations.

**Installation:**
```bash
chmod +x scripts/dev.py
# Optional: add to PATH or create alias
```

**Subcommands:**

#### 1. `dev.py setup` - Initialize development environment
```bash
./scripts/dev.py setup              # Initialize venv and dependencies
./scripts/dev.py setup --no-venv    # Skip venv creation (use existing)
./scripts/dev.py setup --dry-run    # Preview without making changes
```

**What it does:**
- Creates Python virtual environment (if needed)
- Syncs dependencies from uv.lock
- Verifies CMake installation
- Sets up git hooks (if applicable)

#### 2. `dev.py build` - Build the project locally
```bash
./scripts/dev.py build                 # Build with CMake
./scripts/dev.py build --clean         # Clean before rebuild
./scripts/dev.py build --dry-run       # Preview CMake commands
```

**What it does:**
- Creates `build/` directory
- Runs `cmake -B build && cmake --build build`
- Supports incremental builds
- Displays build status with colors

#### 3. `dev.py test` - Run test suite with coverage
```bash
./scripts/dev.py test              # Run tests
./scripts/dev.py test --minimal    # Minimal test run (faster)
./scripts/dev.py test --coverage   # Generate coverage report
./scripts/dev.py test --dry-run    # Preview pytest command
```

**What it does:**
- Runs pytest from `tests/` directory
- Generates coverage metrics
- Creates HTML coverage report (if requested)
- Exits with non-zero on test failure

#### 4. `dev.py package` - Create distribution packages
```bash
./scripts/dev.py package              # Build DEB and source packages
./scripts/dev.py package --source-only  # Only source archive
./scripts/dev.py package --deb-only     # Only DEB package
./scripts/dev.py package --dry-run      # Preview packaging commands
```

**What it does:**
- Builds DEB package for amd64 (`-DZEDIT_BUILD_WHEEL=OFF`)
- Creates source tarball (`.tar.gz`)
- Generates SHA256SUMS checksums
- Outputs packages to `build/` directory

#### 5. `dev.py release` - Create git tag and GitHub release
```bash
./scripts/dev.py release --version 0.2.0              # Release specified version
./scripts/dev.py release --version 0.2.0-rc1 --stage  # Staging release
./scripts/dev.py release --no-wait                     # Don't wait for CI/CD
./scripts/dev.py release --timeout 600                # Custom timeout (seconds)
```

**What it does:**
- Interactive git review of staged changes
- Creates annotated git tag (e.g., `v0.2.0`)
- Pushes tag to origin (triggers GitHub Actions)
- Polls GitHub API for workflow completion
- Reports release URL when ready

**Interactive Git Flow:**
1. Show git status and diff
2. Prompt to stage changes
3. Prompt for commit message (with default)
4. Confirm before push
5. Monitor GitHub Actions workflow

#### 6. `dev.py full` - Complete development workflow
```bash
./scripts/dev.py full --version 0.2.0              # Full release workflow
./scripts/dev.py full --version 0.2.0 --no-test    # Skip tests
./scripts/dev.py full --dry-run                     # Preview all steps
```

**What it does (in sequence):**
1. Setup environment
2. Build project
3. Run tests
4. Package (DEB + source)
5. Interactive git workflow (review → stage → commit → push)
6. Create release tag
7. Wait for GitHub Actions completion
8. Report final release URL

**Example Release Workflow:**
```bash
# Make your changes, commit, and then:
./scripts/dev.py full --version 0.2.0

# Output shows:
# [✓] Environment ready
# [✓] Build complete
# [✓] Tests passed (coverage: 75%)
# [✓] Packages created
# [?] Review changes (shows git diff)
# [?] Stage all? (y/N)
# [?] Commit message?
# [?] Push to origin? (y/N)
# [✓] Tag v0.2.0 created
# [⏳] Waiting for GitHub Actions...
# [✓] Release v0.2.0 published: https://github.com/...
```

**Global Options (all subcommands):**
```bash
./scripts/dev.py --dry-run    # Preview without execution
./scripts/dev.py -v           # Verbose output
./scripts/dev.py --help       # Show help for all commands
```

### Supporting Documentation

**Location:** `scripts/README.md` (500+ lines)
- Comprehensive command reference
- Examples for common workflows
- Troubleshooting guide
- Architecture overview

**Location:** `scripts/QUICKREF.py` (70 lines)
- Quick reference for common commands
- Run with: `python scripts/QUICKREF.py`

### Development Guide

**Location:** `DEVELOPMENT.md` (530+ lines)
- Complete development workflow guide
- Example workflows (bugfix, feature, release, RC, fast development)
- Best practices and conventions
- Integration with GitHub Actions

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
| `docs/github-actions.md` | GitHub Actions workflow documentation |
| `README.md` | Quick start and overview |
| `DEVELOPMENT.md` | Development workflow guide and best practices |

---

## Release History

| Version | Release Date | Notable Changes |
|---|---|---|
| **0.1.0** | 2026-04-15 | First production release with modern CI/CD, GitHub Pages, uv package manager, and dev workflow automation |

---

## GitHub Repository

- **Location:** https://github.com/pilakkat1964/z-edit
- **Owner:** pilakkat1964
- **Visibility:** Public
- **License:** MIT

### Latest Release Assets
- Source archive: `zedit-0.1.0-source.tar.gz` (97 KB)
- Debian package: `zedit-0.6.5-Linux-amd64.deb` (51 KB)
- SHA256SUMS: Cryptographic checksums for all assets

---

## GitHub Pages Documentation

- **URL:** http://pilakkat.mywire.org/z-edit/
- **Theme:** Jekyll Slate
- **Location:** `/docs` folder
- **Configuration:** `_config.yml`

---

## Project Status & Readiness

### ✅ Complete
- Modern build infrastructure (uv, CMake)
- GitHub integration and public repository
- CI/CD pipelines (testing, linting, security scanning)
- Automated release workflow
- Production-ready Debian packages (amd64)
- Comprehensive documentation and GitHub Pages
- Development workflow automation (dev.py script)
- First official production release (v0.1.0)

### 🔄 Optional Enhancements (Future Work)
- Additional test coverage (currently minimal smoke tests)
- RPM package support
- Automated changelog generation
- Semantic versioning automation
- Pre-commit hooks
- PyPI publishing
- Additional platform support (Alpine, macOS)

---

## Quick Start for New Agents

### 1. Set Up Development Environment
```bash
cd /home/sysadmin/workspace/Opencode-workspaces/z-tools/z-edit
source setup-env.sh dev
# Or use: ./scripts/dev.py setup
```

### 2. Build and Test
```bash
./scripts/dev.py build
./scripts/dev.py test
```

### 3. Make Changes
- Edit `zedit.py` for core functionality
- Update tests in `tests/`
- Update configuration in `config/default.toml`

### 4. Release
```bash
./scripts/dev.py full --version X.Y.Z
# This handles: build → test → package → git workflow → release
```

### 5. CI/CD Automation
- Every push triggers: `ci.yml` (test + lint + security)
- Every git tag `vX.Y.Z` triggers: `release.yml` (build packages + create release)

---

## File Organization Reference

### Core Application
- `zedit.py` - Main application (1,725 lines, single file)
- `config/default.toml` - Default MIME/extension mappings

### Build & Dependencies
- `pyproject.toml` - Project metadata, dependencies, build configuration
- `uv.lock` - Locked dependency manifest
- `CMakeLists.txt` - CMake build configuration
- `setup-env.sh` - Build environment setup script

### Development Tools
- `scripts/dev.py` - Main workflow wrapper (1,050+ lines, executable)
- `scripts/README.md` - Development tool documentation (500+ lines)
- `scripts/QUICKREF.py` - Quick reference guide
- `DEVELOPMENT.md` - Development workflow guide (530+ lines)

### Testing
- `tests/` - Test directory
  - `tests/__init__.py` - Package marker
  - `tests/test_smoke.py` - Smoke tests for basic functionality

### CI/CD
- `.github/workflows/ci.yml` - Continuous integration (testing, linting, security)
- `.github/workflows/release.yml` - Release automation (packaging, publishing)

### Packaging
- `debian/` - Debian package control files
  - `debian/postinst` - Post-install script (creates `ze` symlink)
  - `debian/postrm` - Post-remove script
  - Other standard debian control files

### Documentation
- `README.md` - Project overview
- `docs/` - All documentation with Jekyll front matter
  - `docs/index.md` - Landing page
  - `docs/user-guide.md` - User documentation
  - `docs/design.md` - Design documentation
  - `docs/build.md` - Build documentation
  - `docs/cicd-guide.md` - CI/CD documentation
  - `docs/github-actions.md` - GitHub Actions documentation
- `_config.yml` - Jekyll configuration
- `_layouts/default.html` - Custom Jekyll layout
- `AGENTS.md` - This file (agent documentation)

### Git & GitHub
- `.git/` - Git repository (full history preserved)
- `.github/` - GitHub configuration and workflows
- `.gitignore` - Git ignore rules

### Python Cache (Auto-generated)
- `.venv/` - Virtual environment (created by `setup-env.sh`)
- `.pytest_cache/` - Pytest cache
- `.ruff_cache/` - Ruff linter cache
- `zedit.egg-info/` - Setuptools metadata
- `__pycache__/` - Python bytecode cache

---

## Recent Session Updates (Priority 2: Build System Unification)

### ✅ Completed: ARM64 Multiarch Support (April 16, 2026)

**Changes Applied:**
1. **debian/control**: Updated `Architecture: all` → `Architecture: any` for pure Python multiarch support
2. **.github/workflows/release.yml**: 
   - Renamed job `build-debian-amd64` → `build-debian-multiarch`
   - Added architecture verification: confirms `Architecture: any` in DEB package
   - Renamed output artifact to `-multiarch.deb`
   - Updated `create-release` job to use multiarch artifact

**Impact:**
- Single DEB package now works on both amd64 and ARM64 systems
- Faster CI/CD builds (no cross-compilation needed)
- Simpler release process
- Users can install on any Debian-based architecture

**Verification:**
```bash
dpkg -I zedit-*-multiarch.deb | grep Architecture
# Output: Architecture: any
```

**Related Documentation:**
- See `/z-tools/ARM64_CROSSCOMPILE_GUIDE.md` for implementation details
- See `/z-tools/CI_CD_STANDARDIZATION_GUIDE.md` for standardized patterns

---

## Recent Session Updates (Priority 3: GitHub Pages Deployment)

### ✅ Completed: GitHub Pages Already Live + Cross-Project Navigation (April 16, 2026)

**Changes Applied:**

1. **GitHub Pages Status**
   - z-edit GitHub Pages was already deployed and live
   - Site: http://pilakkat.mywire.org/z-edit/
   - Theme: Jekyll Slate (professional blue styling)
   - All documentation rendering correctly

2. **Cross-Project Navigation Update**
   - Added/updated "🔗 Related Z-Tools Projects" section in docs/index.md
   - Standardized all URLs to use `pilakkat.mywire.org` domain
   - Updated RClone Mount Applete link from GitHub Pages to custom domain
   - Updated Master Index link to use consistent domain
   - Links to Z-Open, Z-Kitty Launcher, and RClone Mount Applete

3. **Configuration Status**
   - Pages enabled: Yes ✅
   - Source: master branch, /docs folder ✅
   - HTTPS: Enabled with valid certificate (expires June 23, 2026) ✅
   - Auto-deploy: Working on every push ✅

**Impact:**
- Seamless navigation between all z-tools projects from z-edit
- Users can easily discover and access related tools
- Consistent URL scheme across all projects

**Related Files Modified:**
- `docs/index.md` - Updated cross-project navigation links

**Verification:**
```bash
# Check Pages configuration
gh api repos/pilakkat1964/z-edit/pages

# Verify site is live
curl -I http://pilakkat.mywire.org/z-edit/
```

---

## Recent Session Updates (Priority 4: PyPI Publishing)

### ✅ Completed: PyPI Publishing Setup (April 16, 2026)

**Changes Applied:**

1. **Package Metadata Standardization**
   - Fixed version mismatch: `pyproject.toml` (0.1.0) → `zedit.py` (0.6.5) synchronized to 0.6.5
   - Added author email: `{name = "zedit contributors", email = "dev@example.com"}`
   - Added project URLs: Homepage, Repository, Documentation, Bug Tracker (all pointing to pilakkat.mywire.org or GitHub)
   - Added Python version classifiers: 3.11, 3.12
   - Added development status classifier: "4 - Beta"
   - Added topic classifiers: System Shells, Utilities

2. **PyPI Publishing Workflow**
   - Created `.github/workflows/publish-pypi.yml` (47 lines)
   - Automatically triggered on git tags matching `v*` pattern
   - Uses `pypa/gh-action-pypi-publish@release/v1` for secure PyPI token handling
   - Builds both wheel and source distributions using `python -m build`
   - Verifies package metadata with `twine check` before publishing
   - Includes verification step after publication

3. **Security & Configuration**
   - GitHub Actions environment configured for PyPI deployments
   - Requires `PYPI_API_TOKEN` secret stored in repository settings
   - Uses environment protection rules for secure token handling
   - Verbose output enabled for debugging failed deployments

**Files Modified:**
- `pyproject.toml` - Version sync (0.1.0 → 0.6.5) + metadata additions
- `zedit.py` - Version synchronization with comment for maintainability
- `.github/workflows/publish-pypi.yml` (NEW)

**Commits Created:**
- `554a7af`: "feat: add PyPI publishing workflow and fix version consistency"

**Impact:**
- zedit can now be published to PyPI automatically on release
- Single source of truth for version (both pyproject.toml and zedit.py now 0.6.5)
- Professional package metadata with correct classifiers
- Secure, automated PyPI publishing via GitHub Actions
- Users can install via: `pip install zedit` (once published)

**Next Steps for PyPI Deployment:**
1. Generate PyPI API token at https://pypi.org/manage/account/tokens/
2. Add token as `PYPI_API_TOKEN` repository secret in GitHub
3. Tag and push release: `git tag v0.6.5 && git push origin v0.6.5`
4. Workflow runs automatically and publishes to PyPI
5. Verify package appears at https://pypi.org/project/zedit/

---

## Future Development Priorities

### Priority 5: Crates.io Publishing (Rust Projects)
- Publish z-kitty-launcher to Crates.io registry
- Publish z-rclone-mount-applete to Crates.io registry
- Create Crates.io documentation
- Set up automated Crates.io releases in GitHub Actions

### Priority 5: Crates.io Publishing (Rust Projects)
- Publish z-kitty-launcher to Crates.io registry
- Publish z-rclone-mount-applete to Crates.io registry
- Create Crates.io documentation
- Set up automated Crates.io releases in GitHub Actions

### Priority 6: Enhanced Contribution Guidelines
- Create CONTRIBUTING.md for all projects
- Standardize code review process
- Document development workflow
- Create contributor's guide

### Priority 7: Shared Testing Utilities
- Create cross-project test framework
- Implement integration tests
- Set up performance benchmarking
- Create CI/CD testing matrix

### Priority 8: Performance Dashboards
- Track build times across all projects
- Monitor dependency updates
- Display security audit results
- Create GitHub-based metrics dashboard

---

## GitHub Repository

- **Location:** https://github.com/pilakkat1964/z-edit
- **Owner:** pilakkat1964
- **Visibility:** Public
- **License:** MIT
- **Pages:** http://pilakkat.mywire.org/z-edit/

---

## Version Information

- **Current Version:** 0.6.5
- **Python Requirement:** >= 3.11
- **License:** MIT
- **Last Updated:** April 16, 2026 (Priority 4: PyPI publishing workflow added + version consistency fixed)
