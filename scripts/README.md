# Development Scripts

This directory contains automation scripts for the zedit development workflow.

## dev.py - Development Workflow Wrapper

The main script that wraps the complete development and release cycle.

### Quick Start

```bash
# Set up environment (one time)
./scripts/dev.py setup

# Development cycle
./scripts/dev.py build    # Build locally
./scripts/dev.py test     # Run tests
./scripts/dev.py package  # Build packages

# Release
./scripts/dev.py release --version 0.2.0

# Complete workflow (setup → build → test → package → release)
./scripts/dev.py full --version 0.2.0
```

### Features

- **Environment Setup**: Creates virtual environment and installs dependencies using `uv`
- **Local Building**: CMake-based build with wheel generation disabled (faster packaging)
- **Testing**: Runs pytest with coverage reporting
- **Packaging**: Creates DEB packages and source archives
- **Version Control**: Interactive git review, staging, and commit
- **Release Automation**: Creates git tags and triggers GitHub Actions

### Common Workflows

#### Development Iteration

```bash
# Make changes, then:
./scripts/dev.py build   # Quick rebuild
./scripts/dev.py test    # Run tests
```

#### Prepare Release

```bash
# When ready to release:
./scripts/dev.py full --version 0.2.0

# Or step by step:
./scripts/dev.py build
./scripts/dev.py test
./scripts/dev.py package
./scripts/dev.py release --version 0.2.0
```

#### Staging Release (for QA)

```bash
./scripts/dev.py release --version 0.2.0-rc1 --stage
```

This creates a staging release tag (`v0.2.0-rc1-stage`) for testing before final release.

### Options

Global options:
- `-v, --verbose`: Show all commands being executed
- `--dry-run`: Show what would be done without executing

#### setup

```bash
./scripts/dev.py setup
```

Sets up development environment:
- Creates virtual environment if needed
- Installs dependencies via `uv sync --all-extras`
- Ready for development

#### build

```bash
./scripts/dev.py build
```

Builds the project locally:
- Runs CMake configuration
- Compiles and links
- Suitable for testing locally before packaging

#### test

```bash
./scripts/dev.py test
```

Runs the test suite:
- Executes pytest with verbose output
- Generates coverage reports
- Creates minimal test suite if none exists

#### package

```bash
./scripts/dev.py package [--version VERSION] [--skip-deb] [--skip-source]
```

Creates distributable packages:
- DEB package for Debian/Ubuntu (in `build/`)
- Source archive (.tar.gz)
- Version auto-detected from `pyproject.toml` if not specified

Options:
- `--version`: Override version for source archive
- `--skip-deb`: Skip DEB generation (faster for testing)
- `--skip-source`: Skip source archive (keep DEB only)

#### release

```bash
./scripts/dev.py release [--version VERSION] [--stage] [--no-wait] [--timeout SECONDS]
```

Creates and publishes a release:
1. Reviews git status and prompts to stage changes
2. Creates a commit with release notes
3. Pushes to upstream
4. Creates and pushes git version tag
5. Waits for GitHub Actions to build and publish release

Options:
- `--version`: Override version (default: from `pyproject.toml`)
- `--stage`: Create staging release (adds `-stage` to tag name)
- `--no-wait`: Don't wait for GitHub Actions to complete
- `--timeout SECONDS`: How long to wait for release (default: 300s)
- `--commit-msg`: Custom commit message

#### full

```bash
./scripts/dev.py full [--version VERSION] [--stage] [--no-wait]
```

Runs complete workflow:
1. Sets up environment
2. Builds locally
3. Runs tests
4. Creates packages
5. Creates release

This is the recommended command for releasing new versions.

### Prerequisites

- Python 3.11+
- `uv` package manager (auto-installed via setup)
- `cmake` 3.20+
- `git` with GitHub remote
- `gh` CLI tool (for release automation)
- Build tools: `make`, `gcc` (for building Debian packages)

### Examples

**First time setup:**
```bash
./scripts/dev.py setup
```

**Quick test after changes:**
```bash
./scripts/dev.py build && ./scripts/dev.py test
```

**Release new version (0.2.0):**
```bash
# Update pyproject.toml version first, then:
./scripts/dev.py full --version 0.2.0
```

**Test without actually doing anything:**
```bash
./scripts/dev.py full --version 0.2.0 --dry-run --verbose
```

**Release a release candidate:**
```bash
./scripts/dev.py release --version 0.2.0-rc1 --stage
```

### Troubleshooting

**"Command not found: cmake"**
```bash
# macOS
brew install cmake

# Ubuntu/Debian
sudo apt-get install cmake

# Fedora/RHEL
sudo dnf install cmake
```

**"Command not found: uv"**
The script should install `uv` during setup. If not:
```bash
pip install uv
```

**Virtual environment issues**
```bash
# Recreate environment
rm -rf .venv
./scripts/dev.py setup
```

**Git push fails**
Ensure:
- GitHub remote is configured: `git remote -v`
- SSH key is set up: `git push origin master` (test)
- GitHub token has necessary permissions

### Performance Tips

1. **Use `--skip-deb` during development**: Source archives are faster to create
   ```bash
   ./scripts/dev.py package --skip-deb
   ```

2. **Use `--dry-run` to test workflow**: Before committing to a release
   ```bash
   ./scripts/dev.py full --version 0.2.0 --dry-run --verbose
   ```

3. **Incremental builds**: The build directory is reused between builds
   - Clean with: `rm -rf build/`

### Architecture

The script is structured around a `Context` object that holds:
- Project root directory
- Virtual environment path
- Build directory
- Execution mode (verbose, dry-run)

Commands are implemented as separate functions that operate on the context:
- `cmd_setup()`, `cmd_build()`, etc.
- All use `run_cmd()` for shell execution with consistent logging

### Adding New Commands

To add a new command, follow this pattern:

```python
def cmd_mycommand(args, ctx: Context) -> int:
    """Handle mycommand subcommand."""
    try:
        # Your logic here
        log("Command complete", "success")
        return 0
    except Exception as e:
        log(f"Command failed: {e}", "error")
        return 1

# In main(), add to subparsers:
my_parser = subparsers.add_parser("mycommand", help="Description")
# Add arguments as needed

# Add to commands dict:
"mycommand": cmd_mycommand,
```
