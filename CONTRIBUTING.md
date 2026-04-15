# Contributing to z-edit

Thank you for your interest in contributing to z-edit! This document provides guidelines and instructions for contributing code, documentation, bug reports, and feature suggestions.

## Code of Conduct

Be respectful, inclusive, and professional. All contributors are expected to maintain a welcoming environment for everyone.

## How to Contribute

### 1. Reporting Bugs

**Before submitting a bug report:**
- Check existing issues to avoid duplicates
- Verify the bug still exists on the latest version
- Gather relevant information (version, system, error messages)

**When submitting a bug report, include:**
- Clear title summarizing the issue
- Detailed description with steps to reproduce
- Expected vs. actual behavior
- System information (OS, version, architecture)
- Error messages, logs, or stack traces
- Screenshots if applicable

### 2. Suggesting Features

**Feature suggestions should include:**
- Clear use case explaining why this feature is needed
- Detailed description of expected behavior
- Examples or mockups if applicable
- Discussion of potential implementation approaches
- Links to related discussions or features

### 3. Submitting Code Changes

#### Setup Your Development Environment

```bash
# Clone the repository
git clone git@github.com:pilakkat1964/z-edit.git
cd z-edit

# Set up Python virtual environment
source scripts/activate.sh
# or manually:
uv venv && source .venv/bin/activate

# Install development dependencies
uv sync
# or with pip:
pip install -e ".[dev]"

# Verify setup
python --version
pytest --version
```

#### Development Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   # or for bug fixes:
   git checkout -b fix/issue-number-description
   ```

2. **Make your changes:**
   - Write clear, focused commits with descriptive messages
   - Follow project code style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests and checks:**
   ```bash
   # Run all checks
   ./scripts/dev.py test

   # Or individually:
   pytest                    # Run tests
   ruff check               # Lint check
   ruff format              # Auto-format code
   ```

4. **Commit your changes:**
   ```bash
   git add [files]
   git commit -m "type: brief description

   More detailed explanation if needed.
   - Use bullet points for multiple changes
   - Reference issue numbers: fixes #123"
   ```

   **Commit message guidelines:**
   - Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `style:`, `chore:`
   - First line should be concise (50 chars or less)
   - Provide detailed explanation in the body
   - Reference related issues or PRs

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request:**
   - Clear title describing the change
   - Reference related issues (e.g., "Fixes #123")
   - Describe what changed and why
   - List any breaking changes
   - Include screenshots for UI changes

#### Code Style Guidelines

**z-edit follows these standards:**
- Use Python 3.11+ (tomllib is required)
- Follow PEP 8 style guide
- Use type hints (PEP 484)
- Maximum line length: 100 characters
- Use descriptive variable and function names
- Auto-format with `ruff format`
- Keep `zedit.py` module cohesive and focused

#### Testing Requirements

- Write unit tests for new features
- Ensure all tests pass: `pytest`
- Test both success and error paths
- Include docstring examples if applicable
- Test MIME detection with different file types
- Test configuration merging behavior
- Test editor resolution with various configs

### 4. Documentation Contributions

Documentation improvements are valuable! You can contribute by:

- **Fixing typos and clarifying text** in existing docs
- **Adding examples** to user guides or API documentation
- **Creating new guides** for common use cases
- **Improving architecture documentation** for developers
- **Adding code comments** for complex sections

**Documentation guidelines:**
- Use clear, accessible language
- Include examples and code snippets
- Keep examples up-to-date and tested
- Use consistent formatting and terminology
- Link related documentation sections
- Maintain YAML front matter for Jekyll pages

## Project Structure

```
z-edit/
├── zedit.py                # Main application (1,725 lines)
├── pyproject.toml          # Project configuration
├── setup-env.sh            # Environment setup script
├── CMakeLists.txt          # Build system
├── scripts/
│   ├── dev.py             # Development wrapper
│   ├── activate.sh        # Virtual env setup
│   └── with-venv          # Run commands in venv
├── tests/                 # Test suite
├── debian/                # Debian packaging
├── docs/                  # User documentation
├── _config.yml            # Jekyll configuration
├── .github/workflows/     # CI/CD
├── config/
│   └── default.toml       # Default MIME mappings
├── README.md              # Project overview
├── DEVELOPMENT.md         # Development guide
└── AGENTS.md              # Agent documentation
```

## Building and Testing Locally

```bash
# Setup
source scripts/activate.sh
# or: source setup-env.sh dev

# Build
cmake -B build && cmake --build build
# or: python -m build

# Test
./scripts/dev.py test
# or: pytest

# Run with specific config
python zedit.py --list
python zedit.py --init-config

# Package
./scripts/dev.py package
# or: cmake --build build --target package
```

## Understanding the Codebase

### Main Components

1. **Configuration Subsystem** (lines ~100-400)
   - `load_config()` - Load and merge configurations
   - `_parse_toml_file()` - Parse TOML configuration
   - `_deep_merge()` - Recursively merge config layers

2. **MIME-Type Detection** (lines ~400-500)
   - `detect_mime()` - Detect file MIME types
   - Uses `python-magic` (preferred) or `mimetypes` stdlib

3. **Editor Resolution** (lines ~500-700)
   - `resolve_editor()` - Map MIME type → editor command
   - Priority-based resolution algorithm

4. **CLI Subsystem** (lines ~700-1725)
   - `build_parser()` - CLI argument parsing
   - `main()` - Main entry point and control flow
   - Various interactive modes (--list, --choose, --map, etc.)

### Key Functions to Know

- `main()` - Entry point and application control flow
- `load_config()` - Core configuration management
- `detect_mime()` - MIME type detection logic
- `resolve_editor()` - Editor selection algorithm
- `write_default_config()` - Generate default configuration

## Release Process

### Versioning

Uses [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes to config format or CLI
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes and documentation

### Creating a Release

1. **Update version** in both `pyproject.toml` and `zedit.py`
2. **Update changelog** in docs or git history
3. **Commit changes**: `git commit -m "chore: bump version to X.Y.Z"`
4. **Create git tag**: `git tag vX.Y.Z -m "Release vX.Y.Z"`
5. **Push to remote**: `git push origin master && git push origin vX.Y.Z`
6. **GitHub Actions will automatically:**
   - Run tests and security checks
   - Build wheel and source distributions
   - Build Debian packages
   - Create GitHub Release
   - Publish to PyPI

See `AGENTS.md` for detailed release procedures.

## Getting Help

- **Documentation**: See `docs/` folder - start with `user-guide.md`
- **Architecture**: See `AGENTS.md` and `docs/design.md`
- **Development**: See `DEVELOPMENT.md`
- **Issues**: Check existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Examples**: See `docs/examples.md`

## License

By contributing to z-edit, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are valued and recognized! We may mention contributors in:
- Release notes
- Project README
- Contributor list

Thank you for contributing to z-edit! 🙏
