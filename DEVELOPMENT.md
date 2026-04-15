# Z-Edit Development Workflow - Complete Guide

## Overview

The z-edit project now includes a comprehensive development workflow wrapper (`./scripts/dev.py`) that accelerates the test-driven development cycle by automating:

1. **Environment Setup** - Virtual environment + dependency installation
2. **Building** - Local CMake builds for testing
3. **Testing** - Automated test suite execution with coverage
4. **Packaging** - DEB packages and source archives
5. **Version Control** - Interactive git review, staging, and commits
6. **Release** - Automated GitHub release creation and CI/CD integration

## Quick Start

### First Time Setup

```bash
# Clone the repository and enter directory
git clone git@github.com:pilakkat1964/z-edit.git
cd z-edit

# Set up development environment
./scripts/dev.py setup

# Verify setup works
./scripts/dev.py build
./scripts/dev.py test
```

### Daily Development

```bash
# Make your changes to zedit.py, CMakeLists.txt, etc.

# Test locally
./scripts/dev.py build && ./scripts/dev.py test

# Create packages and review them
./scripts/dev.py package

# Or all in one go
./scripts/dev.py build && ./scripts/dev.py test && ./scripts/dev.py package
```

### Create a Release

```bash
# When ready to release version 0.2.0
./scripts/dev.py full --version 0.2.0

# This runs the complete workflow:
# 1. Builds locally
# 2. Runs tests
# 3. Creates packages (DEB + source)
# 4. Reviews git changes interactively
# 5. Creates a commit
# 6. Creates git tag v0.2.0
# 7. Waits for GitHub Actions to build release

# View the released version at:
# https://github.com/pilakkat1964/z-edit/releases/tag/v0.2.0
```

## Command Reference

### `dev.py setup`

**Purpose**: Initialize development environment

```bash
./scripts/dev.py setup
```

Creates:
- Virtual environment in `.venv/`
- Installs all dependencies via `uv sync --all-extras`
- Ready for development and testing

**When to use**: First time only, or when dependencies change

---

### `dev.py build`

**Purpose**: Compile project locally for testing

```bash
./scripts/dev.py build
```

What it does:
- Removes previous build directory (if exists)
- Runs CMake configuration with `-DZEDIT_BUILD_WHEEL=OFF` (faster packaging builds)
- Compiles and links all targets
- Creates build artifacts in `./build/` directory

**When to use**: After making code changes, before testing/packaging

---

### `dev.py test`

**Purpose**: Run the test suite with coverage reporting

```bash
./scripts/dev.py test
```

What it does:
- Checks for `tests/` directory (creates with minimal tests if missing)
- Runs pytest with verbose output
- Generates coverage report showing untested code
- Auto-creates `test_smoke.py` if no tests exist

**When to use**: After building, before committing changes

**Sample output**:
```
tests/test_smoke.py::test_zedit_module_imports PASSED    [ 50%]
tests/test_smoke.py::test_version_exists PASSED          [100%]

Name       Stmts   Miss  Cover   Missing
----------------------------------------
zedit.py     615    560     9%   37-41, 46-47, ...
```

---

### `dev.py package`

**Purpose**: Create distributable packages

```bash
./scripts/dev.py package [--version VERSION] [--skip-deb] [--skip-source]
```

Creates:
- **DEB package** - `zedit-0.6.5-Linux-amd64.deb` (in `build/`)
- **Source archive** - `zedit-0.1.0-source.tar.gz` (root directory)

Options:
- `--version VERSION`: Override version (auto-detected from pyproject.toml if not given)
- `--skip-deb`: Skip DEB generation (faster for testing)
- `--skip-source`: Skip source archive (keep DEB only)

**When to use**: Before releases, to verify packages build correctly

**Example - Quick packaging (DEB only)**:
```bash
./scripts/dev.py package --skip-source
```

---

### `dev.py release`

**Purpose**: Create and publish a release

```bash
./scripts/dev.py release [--version VERSION] [--stage] [--no-wait] [--commit-msg MSG]
```

Complete release workflow:
1. Reviews git status (shows modified files)
2. **Interactive**: Prompts to stage changes
3. Creates commit with release notes
4. Pushes to upstream
5. Creates git tag `v0.2.0`
6. Pushes tag to trigger GitHub Actions
7. Waits for GitHub Actions to complete (polls every 10 seconds)
8. Shows release URL when done

Options:
- `--version VERSION`: Release version (default: from pyproject.toml)
- `--stage`: Creates staging tag (adds `-stage` suffix for QA testing)
- `--no-wait`: Don't wait for GitHub Actions (fire and forget)
- `--commit-msg MSG`: Custom commit message
- `--timeout SECONDS`: How long to wait (default: 300s = 5 min)

**Example - Release v0.2.0**:
```bash
./scripts/dev.py release --version 0.2.0
```

**Example - Staging release for QA**:
```bash
./scripts/dev.py release --version 0.2.0-rc1 --stage
```
Creates tag `v0.2.0-rc1-stage` for testing before final release.

**What happens in GitHub**:
1. Release workflow triggers automatically when tag is pushed
2. Builds DEB package (amd64)
3. Creates source archive
4. Generates SHA256SUMS checksums
5. Creates GitHub Release with all assets
6. Release is published at: `github.com/pilakkat1964/z-edit/releases/tag/v0.2.0`

---

### `dev.py full`

**Purpose**: Complete workflow from build to release

```bash
./scripts/dev.py full [--version VERSION] [--stage] [--no-wait]
```

Runs all steps in sequence:
1. **Build** - Compiles locally
2. **Test** - Runs test suite
3. **Package** - Creates DEB + source
4. **Release** - Creates tag and publishes

Options: Same as `release` command

**Example - Release v0.2.0 completely**:
```bash
./scripts/dev.py full --version 0.2.0
```

**Example - Dry run to test workflow**:
```bash
./scripts/dev.py --dry-run --verbose full --version 0.2.0
```
Shows all commands without executing anything.

---

## Global Options

These apply to all commands:

```bash
./scripts/dev.py [OPTIONS] COMMAND [COMMAND_OPTIONS]
```

- `-v, --verbose`: Show all commands being executed (useful for debugging)
- `--dry-run`: Show what would be done without making any changes (test mode)

**Example - Verbose release**:
```bash
./scripts/dev.py --verbose release --version 0.2.0
```
Shows every command being executed.

**Example - Test workflow without changes**:
```bash
./scripts/dev.py --dry-run full --version 0.2.0
```

---

## Typical Development Workflows

### Workflow 1: Bug Fix

```bash
# Make changes to zedit.py
# ... edit zedit.py ...

# Test locally
./scripts/dev.py build && ./scripts/dev.py test

# If tests pass, commit and push
git add zedit.py
git commit -m "fix: handle edge case in MIME detection"
git push origin master
```

### Workflow 2: Feature Development

```bash
# Branch for feature
git checkout -b feature/better-editor-selection

# Make changes
# ... edit zedit.py, CMakeLists.txt, config/ ...

# Test iteratively
./scripts/dev.py build
./scripts/dev.py test
# ... fix issues ...
./scripts/dev.py build && ./scripts/dev.py test

# Create PR
git add .
git commit -m "feat: add fuzzy editor selection with fzf"
git push origin feature/better-editor-selection
# Create PR on GitHub

# After merge to master
git checkout master
git pull origin master
```

### Workflow 3: Release New Version

```bash
# Ensure everything is committed
git status  # Should be clean

# Update version in pyproject.toml
# ... edit pyproject.toml: version = "0.2.0" ...

# Complete release workflow
./scripts/dev.py full --version 0.2.0

# Verify release at GitHub
open https://github.com/pilakkat1964/z-edit/releases/tag/v0.2.0
```

### Workflow 4: Release Candidate (QA Testing)

```bash
# Create RC build for testing
./scripts/dev.py release --version 0.2.0-rc1 --stage

# This creates: v0.2.0-rc1-stage tag
# Available at: github.com/pilakkat1964/z-edit/releases/tag/v0.2.0-rc1-stage

# QA team tests the release
# ... QA testing happens ...

# If issues found, fix them and create new RC
./scripts/dev.py release --version 0.2.0-rc2 --stage

# When ready for production
./scripts/dev.py release --version 0.2.0
```

### Workflow 5: Fast Development (Packaging Only)

```bash
# During development, just build packages quickly
./scripts/dev.py package --skip-source  # Only DEB

# Or
./scripts/dev.py package --skip-deb     # Only source
```

---

## Integration with CI/CD

The script integrates with GitHub Actions:

**When you push a release tag:**
```bash
./scripts/dev.py release --version 0.2.0
# Pushes tag v0.2.0 to GitHub
```

**GitHub Actions automatically:**
1. Detects the tag
2. Runs the Release workflow
3. Builds DEB package
4. Creates source archive
5. Generates SHA256SUMS checksums
6. Creates GitHub Release with all assets

**What you get in the release:**
- `zedit-0.2.0-source.tar.gz` - Source code archive
- `zedit-0.6.5-Linux-amd64.deb` - Debian package
- `SHA256SUMS` - Checksums for verification

**Verify the release:**
```bash
# Download SHA256SUMS and packages
cd /tmp
gh release download v0.2.0 --repo pilakkat1964/z-edit

# Verify checksums
sha256sum -c SHA256SUMS
```

---

## Troubleshooting

### Problem: "Command not found: cmake"

**Solution**: Install CMake

```bash
# macOS
brew install cmake

# Ubuntu/Debian
sudo apt-get update && sudo apt-get install cmake

# Fedora/RHEL
sudo dnf install cmake
```

### Problem: "uv command not found"

**Solution**: `uv` is installed during setup. If not:

```bash
pip install uv
# Then run setup again
./scripts/dev.py setup
```

### Problem: Virtual environment issues

**Solution**: Recreate the environment

```bash
rm -rf .venv
./scripts/dev.py setup
```

### Problem: "Git push failed"

**Solution**: Verify GitHub access

```bash
# Test SSH connection
ssh git@github.com

# Or test HTTPS
git remote -v  # Should show GitHub remote

# Ensure SSH key is set up
ssh-add ~/.ssh/id_ed25519
```

### Problem: Tests fail

**Solution**: Check test output

```bash
# Run tests with verbose output
./scripts/dev.py test

# Or with your custom test command
python -m pytest tests/ -v --tb=short
```

### Problem: "Release creation timeout"

**Solution**: GitHub Actions is still building. Check manually:

```bash
# View release page
open https://github.com/pilakkat1964/z-edit/releases/tag/v0.2.0

# Or use gh CLI
gh release view v0.2.0 --repo pilakkat1964/z-edit

# Check Actions
gh run list --repo pilakkat1964/z-edit --workflow release.yml
```

---

## Architecture

The script is designed for maintainability:

**Core Components:**
- `Context` class: Holds project paths and execution state
- `run_cmd()`: Unified command execution with logging
- Command functions: `cmd_setup()`, `cmd_build()`, etc.
- Color logging: ANSI colored output for clarity

**Key Design Decisions:**
- No external dependencies (except uv which is installed)
- Dry-run mode for testing workflows
- Interactive prompts for critical operations (git staging)
- Comprehensive error handling
- Clear logging with color codes

**Adding New Commands:**
See `scripts/README.md` for examples.

---

## Performance Tips

1. **Fast development cycle**:
   ```bash
   ./scripts/dev.py package --skip-source  # Skip source archive
   ```

2. **Test workflow before committing**:
   ```bash
   ./scripts/dev.py --dry-run full --version 0.2.0
   ```

3. **Reuse build directory**: Don't delete `build/` between builds
   (Incremental builds are much faster)

4. **Parallel testing**: pytest runs tests in parallel by default
   (you can customize with `pytest.ini_options` in pyproject.toml)

---

## Related Files

- `scripts/dev.py` - Main workflow script (this reference)
- `scripts/README.md` - Detailed command documentation
- `scripts/QUICKREF.py` - Quick reference with examples
- `pyproject.toml` - Project metadata and dependencies
- `.github/workflows/release.yml` - GitHub Actions release workflow
- `CMakeLists.txt` - Build configuration
- `tests/` - Test suite directory

---

## Support

For issues or questions:
1. Check `scripts/README.md` for detailed command docs
2. Run with `--verbose` to see all commands
3. Try `--dry-run` to test without changes
4. Check GitHub Issues: https://github.com/pilakkat1964/z-edit/issues

---

## Version

Created: 2026-04-15  
Script Version: 1.0.0  
Compatible with: zedit 0.1.0+, Python 3.11+
