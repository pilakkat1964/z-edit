# Z-Edit Development Workflow - Complete Guide

## Overview

The z-edit project is a smart file editor launcher that automatically opens files in the appropriate editor based on MIME type (auto-detected or explicitly specified) or file extension. This guide covers the development workflow for contributing to z-edit.

### Architecture

Z-Edit maintains a single-file deployment model while providing comprehensive functionality:

- **Single-file module**: `zedit.py` (1,725 lines) contains the entire application
- **Zero hard dependencies**: Works with Python 3.11+ stdlib alone
- **Optional MIME detection**: `python-magic` for accurate content-based type detection
- **Configuration layers**: System-wide → user-global → project-local → ad-hoc overrides

This design ensures simplicity for deployment while maintaining power and flexibility.

## Quick Start

### ⚡ Quickest Path (Automated with dev.py)

Z-Edit includes `scripts/dev.py`, a workflow wrapper that automates virtual environment setup and common tasks:

```bash
# Clone the repository and enter directory
git clone git@github.com:pilakkat1964/z-edit.git
cd z-edit

# One-time setup (creates venv with uv or standard venv, installs dependencies)
./scripts/dev.py setup

# Test your changes
./scripts/dev.py test

# When ready to release
./scripts/release.py 0.6.6
```

See `scripts/README.md` for complete documentation on all available commands.

### Manual Virtual Environment Setup

If you prefer to manage the virtual environment yourself:

#### **Option 1: Using uv (Fast & Recommended)**

**Benefits:** 10-100x faster than pip, zero external dependencies, automatic venv management

First, [install uv](https://docs.astral.sh/uv/getting-started/):

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with homebrew
brew install uv

# Or with pip
pip install uv
```

Then set up z-edit:

```bash
# Clone the repository
git clone git@github.com:pilakkat1964/z-edit.git
cd z-edit

# Use the provided activation script (automatic venv setup with uv)
source scripts/activate.sh

# Or manually with uv:
uv venv --python 3.11        # Create venv
source .venv/bin/activate    # Activate
uv pip install -e ".[dev]"   # Install dependencies

# Verify setup
python --version
python zedit.py --help
```

**Using uv for package management:**

```bash
# Install new packages
uv pip install package-name

# Install from wheel
uv pip install dist/zedit-0.6.5-py3-none-any.whl

# Install with extras
uv pip install ".[magic]"

# Run Python without explicit activation
uv run python zedit.py --help
```

#### **Option 2: Using standard venv**

```bash
# Clone the repository
git clone git@github.com:pilakkat1964/z-edit.git
cd z-edit

# Create virtual environment manually
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies with pip
pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"

# Verify setup
python zedit.py --help
python zedit.py --list
```

### Running Commands in Virtual Environment

Once your venv is set up, use one of these approaches:

**Approach 1: Activate then run with uv (recommended for interactive development)**
```bash
source scripts/activate.sh
# Then use uv pip for fast package management
uv pip install package-name
python zedit.py --help
pytest
cmake --build build --target deb
```

**Approach 2: Use uv run (no activation needed)**
```bash
# Run commands directly in venv without activation
uv run python zedit.py --help
uv run pytest
uv run python -c "from zedit import load_config; print(load_config())"
```

**Approach 3: Use the with-venv wrapper (for one-off commands)**
```bash
scripts/with-venv python zedit.py --help
scripts/with-venv pytest
scripts/with-venv uv pip install somepackage
```

**Approach 4: Use dev.py wrapper (for release workflows)**
```bash
./scripts/dev.py test
./scripts/dev.py build
./scripts/release.py 0.6.6
```

## Virtual Environment Management

### ⚠️ Important: Always Use Virtual Environment

The project **must** use a virtual environment for:
- ✅ **Portability** - Works across different systems without system Python conflicts
- ✅ **Consistency** - Same dependencies in CI/CD and local development
- ✅ **Isolation** - Project dependencies don't affect system Python
- ✅ **Reproducibility** - Exact same environment for all developers

### Automatic Setup

The `scripts/activate.sh` script automatically:
1. Checks if `.venv` exists
2. Creates it using `uv` (if available) or standard `venv`
3. Installs/upgrades pip, setuptools, wheel
4. Installs project dependencies from `pyproject.toml[dev]`
5. Activates the virtual environment

```bash
# Automatic setup
source scripts/activate.sh
```

### Manual Setup

If you need to set it up manually:

```bash
# Using uv (fast, recommended)
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[dev]"

# Or using standard venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Verification

After setup, verify everything works:

```bash
# Check Python version
python --version  # Should be 3.11+

# Check venv location
which python      # Should show path to .venv/bin/python

# Run basic tests
python zedit.py --help
python zedit.py --version
python -m pytest --version
```

### Daily Development

Using the wrapper:

```bash
# Make changes to zedit.py or config files

# Test your changes
./scripts/dev.py test

# Create packages and review
./scripts/dev.py package
```

Or manually (if not using the wrapper):

```bash
# Make changes to zedit.py or config files

# Test manually
python zedit.py --help
python zedit.py --list
python zedit.py --dump /etc/hosts

# For configuration changes, test the config system
python -c "from zedit import resolve_editor; print(resolve_editor('/etc/hosts'))"
```

### Create a Release

Using the wrapper (recommended):

```bash
# Run complete workflow: test → build → package → release
./scripts/dev.py full --version 0.6.6

# Or just create a release (if you've already tested)
./scripts/release.py 0.6.6

# View the released version at:
# https://github.com/pilakkat1964/z-edit/releases/tag/v0.6.6
```

Manual process:

```bash
# Update version in pyproject.toml
# Add release notes to docs/CHANGELOG.md (or README.md)

# Create a tag and push (GitHub Actions handles the rest)
git tag v0.6.6
git push origin master
git push origin v0.6.6

# View the released version at:
# https://github.com/pilakkat1964/z-edit/releases/tag/v0.6.6
```

## Development Workflow Patterns

### Bug Fix Workflow

```bash
# 1. Create a branch for the bug
git checkout -b fix/issue-description

# 2. Make changes to zedit.py
# - Find the relevant section (use grep: grep -n "def function_name" zedit.py)
# - Make minimal, focused changes

# 3. Test the fix manually
python zedit.py [relevant command/option]

# 4. Review changes
git diff zedit.py

# 5. Commit
git commit -am "fix: brief description of bug and solution"

# 6. Push and create PR
git push origin fix/issue-description
gh pr create --title "Fix: ..." --body "Fixes #123"
```

### Feature Addition Workflow

```bash
# 1. Create a branch for the feature
git checkout -b feature/feature-name

# 2. Plan the implementation:
#    - Which section should be modified?
#    - Does it need a new function?
#    - Will it affect configuration?

# 3. Implement incrementally
#    - Add the core functionality
#    - Add docstrings
#    - Add error handling

# 4. Test thoroughly
python zedit.py [test the new feature]

# 5. Update documentation if needed
#    - docs/design.md (architecture changes)
#    - README.md (usage examples)
#    - docs/user-guide.md (user-facing features)

# 6. Commit and push
git commit -am "feat: description of new feature"
git push origin feature/feature-name
gh pr create --title "Feature: ..." --body "Adds support for ..."
```

### Configuration Extension Workflow

```bash
# Adding new editor mappings or MIME handlers

# 1. Create a branch
git checkout -b config/add-mappings

# 2. Update config files in config/ directory
#    - config/default.toml: Add editor mappings

# 3. Test the new configuration
python -c "from zedit import load_config, resolve_editor; \
    config = load_config(); \
    editor = resolve_editor('/etc/some.file'); \
    print('Resolved editor:', editor)"

# 4. Verify z-edit uses the new mappings
python zedit.py --list

# 5. Document in README.md if it's a user-facing addition
# 6. Commit and push
git commit -am "config: add support for new editor mappings"
```

## Architecture Understanding

### Key Sections and Functions

**zedit.py** contains ~1,725 lines organized in these sections:

#### Configuration Subsystem (Lines ~100-400)
- `_parse_toml_str()` - Parse TOML from string
- `_parse_toml_file()` - Parse TOML from file
- `_deep_merge()` - Recursively merge configuration dictionaries
- `load_config()` - Load and merge config from all priority locations

#### MIME-Type Detection Subsystem (Lines ~400-500)
- `detect_mime()` - Detect file MIME types using available methods

#### Editor Resolution Subsystem (Lines ~500-700)
- `resolve_editor()` - Resolve the editor command for a file
- `_resolve_sentinel()` - Resolve `$EDITOR` to actual command

#### CLI Subsystem (Lines ~700-1725)
- `build_parser()` - Create argument parser
- `main()` - Main entry point and control flow
- `write_default_config()` - Generate starter config template
- `print_mappings()` - Display configured mappings

Find functions using:
```bash
grep -n "^def " zedit.py
```

### Common Modifications

**To add a new configuration location:**
```python
# In load_config(), add a new tuple to the config_paths list
config_paths = [
    _DEFAULT_CONFIG_TOML,
    "/opt/etc/zedit/config.toml",
    "~/.config/zedit/config.toml",
    "./.zedit.toml",
    # Add new location here
]
```

**To add a new MIME detection method:**
```python
# In detect_mime(), add a new detection strategy
def detect_mime(filepath):
    # Try python-magic first
    if _HAVE_LIBMAGIC:
        # ...use libmagic
    # Then try new method
    # Finally fall back to extension
```

**To add a new CLI flag:**
```python
# In build_parser(), add the flag to the parser
parser.add_argument(
    '--new-flag',
    action='store_true',
    help='Description of the new flag'
)
# Then handle it in main()
```

## Testing

### Local Testing Guide

Before committing changes, ensure you're in the virtual environment and run the following tests:

#### **Quick Verification** (for small changes)

```bash
# Activate venv first
source scripts/activate.sh

# Basic functionality check
python zedit.py --help
python zedit.py --version

# Quick editor resolution check
python zedit.py --dump /etc/hosts
```

#### **Full Testing Workflow** (before committing)

**Step 1: Run Unit Tests (if available)**

```bash
# If tests exist in tests/ directory
scripts/with-venv pytest -v

# Or if you have activated the venv
pytest -v

# Run with coverage report
pytest --cov=zedit --cov-report=html
# View report at htmlcov/index.html
```

**Step 2: Manual CLI Testing**

```bash
# Test core commands
python zedit.py --help
python zedit.py --version
python zedit.py --list

# Test MIME detection
python zedit.py --dry-run /etc/hosts
python zedit.py --dump /etc/hosts
python zedit.py --dump ~/.bashrc

# Test configuration
python zedit.py --init-config  # Create user config
python zedit.py --list          # Show mappings
```

**Step 3: Test Configuration Changes**

If you modified config files or configuration logic:

```bash
# Verify configuration loads without errors
python -c "from zedit import load_config; \
    config = load_config(); \
    print('Loaded configuration successfully')"

# Check specific configuration
python -c "from zedit import load_config, resolve_editor; \
    config = load_config(); \
    editor = resolve_editor('/etc/hosts'); \
    print('Resolved editor:', editor)"
```

**Step 4: Test Code Changes**

For changes to specific functions:

```bash
# Test MIME detection
python -c "from zedit import detect_mime; \
    mime = detect_mime('/etc/hosts'); \
    print('Detected MIME type:', mime)"

# Test editor resolution
python -c "from zedit import resolve_editor; \
    editor = resolve_editor('/etc/hosts'); \
    print('Resolved editor:', editor)"
```

#### **Full Regression Test Checklist**

Before creating a release, run this complete checklist:

```bash
# Ensure you're in the venv
source scripts/activate.sh

# 1. Run automated tests (if available)
pytest -v --tb=short

# 2. Check linting (if available)
ruff check zedit.py

# 3. Test all CLI commands
python zedit.py --help
python zedit.py --version
python zedit.py --list
python zedit.py --dry-run /etc/hosts
python zedit.py --dump /etc/hosts

# 4. Build packages
mkdir -p build
cd build
cmake ..
make package
ls -lah *.deb
cd ..

# 5. Test package installation (optional, if you want to test the actual installer)
# sudo dpkg -i build/*.deb
# zedit --help
# sudo dpkg -r zedit
```

#### **Automated Test Execution**

Using the dev.py wrapper for automated testing:

```bash
# Run just the tests
./scripts/dev.py test

# Run full workflow (test → build → package)
./scripts/dev.py full --version 0.6.6

# View available dev.py commands
./scripts/dev.py help
```

### Manual Testing Checklist (Quick Reference)

Before committing changes:

```bash
# 1. Basic functionality
python zedit.py --help
python zedit.py --version

# 2. List mappings
python zedit.py --list

# 3. Test file opening (dry-run)
python zedit.py --dry-run /etc/hosts
python zedit.py --dump /etc/hosts

# 4. Configuration
python zedit.py --init-config
python zedit.py --list
```

## Build and Packaging

### Local Build

```bash
# CMake is used for packaging and distribution
mkdir -p build
cd build
cmake ..
make
cd ..

# Creates DEB package in build/
ls -la build/*.deb
```

### Creating Release Packages

GitHub Actions automatically creates packages on release:

1. **DEB Package**: `zedit-VERSION-Linux-amd64.deb`
   - Installs zedit.py to `/usr/local/bin/`
   - Installs man page
   - Includes dependencies

2. **Source Archive**: `zedit-VERSION-source.tar.gz`
   - Complete source code
   - CMakeLists.txt, config files, documentation

### Manual Package Creation

```bash
# Build locally
cd build
cmake ..
make package

# Creates .deb package
ls *.deb
```

## Version Management

Version is defined in `pyproject.toml`:

```toml
[project]
version = "0.6.6"
```

When releasing:

1. Use `./scripts/release.py 0.6.6` to automatically update version and create tag
2. Or manually update version in `pyproject.toml`, create tag, and push
3. GitHub Actions automatically creates the release

## Documentation

### Files to Update

When making changes, update relevant documentation:

- **README.md**: User-facing features and usage
- **docs/user-guide.md**: Detailed usage instructions
- **docs/design.md**: Architecture and design decisions
- **docs/build.md**: Build and compilation instructions
- **docs/github-actions.md**: CI/CD and release process
- **DEVELOPMENT.md** (this file): Development workflow

### Running Docs Locally

```bash
# Docs use Jekyll Slate theme
# Preview at: https://pilakkat1964.github.io/z-edit/

# Or build locally (requires Jekyll)
cd docs
bundle install
bundle exec jekyll serve --source . --destination ../_site
# View at http://localhost:4000/z-edit/
```

## GitHub Actions and CI/CD

### Release Workflow (`.github/workflows/release.yml`)

Triggered when you push a git tag (e.g., `v0.6.6`):

1. Builds DEB package for Linux amd64
2. Creates source archive
3. Generates SHA256SUMS checksums
4. Creates GitHub Release with all assets
5. Publishes to releases page

### GitHub Pages Workflow (`.github/workflows/pages.yml`)

Automatically triggered when docs are updated:

1. Builds Jekyll from `/docs` folder
2. Deploys to GitHub Pages
3. Available at: https://pilakkat1964.github.io/z-edit/

### CI Workflow (`.github/workflows/ci.yml`)

Runs on every push and pull request:

- Test on Python 3.11, 3.12, 3.13
- Linting with ruff
- Security scanning with bandit
- Coverage reports

## Common Tasks

### View Recent Commits

```bash
git log --oneline -10
```

### Check Branch Status

```bash
git status
git branch -a
```

### Review Changes Before Commit

```bash
git diff zedit.py
git diff config/
```

### Undo Changes

```bash
# Undo unstaged changes
git checkout zedit.py

# Undo staged changes
git reset HEAD zedit.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

### Merge Latest Changes

```bash
# Update master from remote
git fetch origin
git merge origin/master

# Or rebase your branch
git rebase origin/master
```

## Troubleshooting

### Import Errors

```bash
# If zedit.py can't be imported:
# 1. Ensure Python 3.11+ is used
python3 --version

# 2. Check if zedit.py is in the current directory
ls -la zedit.py

# 3. Try running directly
python3 zedit.py --help
```

### Configuration Issues

```bash
# If config loading fails:
python zedit.py --list

# Enable verbose output (if implemented):
python zedit.py --verbose --list
```

### Editor Resolution Issues

```bash
# Test editor resolution
python zedit.py --dump /path/to/file

# Check what editor would be used
python -c "from zedit import resolve_editor; print(resolve_editor('/etc/hosts'))"
```

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions about development
- **Code Comments**: Read inline documentation in zedit.py
- **AGENTS.md**: Comprehensive project architecture guide

## Code Style

Z-Edit follows these conventions:

- **Python**: PEP 8, 4-space indentation
- **Naming**: snake_case for functions/variables, CamelCase for classes
- **Docstrings**: Include for all public functions and classes
- **Comments**: Explain "why", not "what"
- **Line Length**: Max 100 characters (match existing code)

Example:

```python
def my_function(param1, param2):
    """Brief description of what the function does.
    
    Longer description if needed, explaining the purpose
    and usage of this function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
    """
    # Do work
    return result
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes following the workflow patterns above
4. Test thoroughly
5. Commit with clear messages
6. Push to your fork
7. Create a pull request

See GitHub for current issues and feature requests.

---

**Last Updated:** 2026-04-16  
**Z-Edit Version:** 0.6.5  
**Python Support:** 3.11+  
**Project:** Smart file editor launcher with MIME-type aware editor selection
