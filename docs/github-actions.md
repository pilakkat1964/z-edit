---
layout: default
title: GitHub Actions CI/CD
description: Continuous Integration and Automated Release Workflows
---

# GitHub Actions CI/CD Pipeline

Comprehensive continuous integration and automated release workflows for z-edit.

## Overview

The project includes two main GitHub Actions workflows:

1. **CI Workflow** - Runs on every push and pull request
2. **Release Workflow** - Runs on version tags, creates multi-platform releases

## CI Workflow

### Triggers

- **Push**: On push to `master` or `develop` branches
- **Pull Request**: On pull requests to `master` or `develop` branches
- **Paths**: Ignores documentation and markdown changes for efficiency

### Jobs

#### 1. Lint and Test

**Purpose**: Validate code quality and run tests

**Environment**:
- Ubuntu Latest
- Python 3.11 and 3.12 (matrix)

**Steps**:
- Checkout code
- Set up Python (matrix versions)
- Install uv package manager
- Install dependencies with `uv sync --all-extras`
- Run linting with ruff (if installed)
- Execute pytest test suite
- Verify zedit runs correctly
- Type checking (optional)

**Continue on Error**: 
- Linting failures don't block builds
- Type checking is optional
- Missing tests directory is handled gracefully

#### 2. Security Check

**Purpose**: Scan for vulnerabilities

**Steps**:
- Scan filesystem with Trivy vulnerability scanner
- Generate SARIF results
- Upload to GitHub Security tab

**Continue on Error**: Security scanning failures don't block workflow

#### 3. Build Check

**Purpose**: Verify build artifacts are created correctly

**Environment**:
- Ubuntu Latest
- Python 3.11

**Dependencies**:
- CMake
- python3-magic

**Steps**:
- Configure CMake build
- Build source archive (tarball)
- Verify archive integrity
- Extract and inspect contents
- Test installation from extracted archive

## Release Workflow

### Triggers

- **Push**: On push of version tags matching pattern `v*`
  - Example: `v0.1.0`, `v1.2.3`

### Version Format

Tags must follow semantic versioning:
- Format: `vX.Y.Z` (e.g., `v0.6.5`)
- Validation: Enforced by workflow

### Release Jobs

#### 1. Prepare Job

**Output**: Version number extracted from tag

**Steps**:
- Extract version from git tag (removes 'v' prefix)
- Validate version follows semantic versioning
- Output version for use by other jobs

#### 2. Build Source Package

**Output**: 
- `zedit-X.Y.Z-source.tar.gz`
- SHA256 checksum

**Steps**:
- Checkout code with full history
- Create git archive with tag prefix
- Verify archive creation
- Upload as artifact (7-day retention)

**Contents**:
- All source files
- Documentation
- Build configuration
- Git history metadata

#### 3. Build Debian AMD64

**Output**: 
- `zedit-X.Y.Z-amd64.deb`
- Checksums

**Platform**: AMD64/x86_64

**Steps**:
- Install build dependencies:
  - cmake
  - python3-magic
  - dpkg-dev
  - debhelper
  - dh-python
- Configure CMake
- Build Debian package
- Rename package with -amd64 suffix
- Verify package integrity with `dpkg -I`
- Upload as artifact

**Package Details**:
- Architecture: all (Python-based)
- Depends: Python 3.11+, python3-magic (recommended)
- Installs to: /opt/zedit

#### 4. Build Debian ARM64

**Output**: 
- `zedit-X.Y.Z-arm64.deb`
- Checksums

**Platform**: ARM64/aarch64

**Method**: Docker + QEMU (linux/arm64 platform)

**Steps**:
- Set up QEMU for arm64 emulation
- Set up Docker Buildx for multi-platform
- Create ARM64 Dockerfile with build environment
- Build using `docker buildx` with `--platform linux/arm64`
- Extract deb from Docker image
- Rename package with -arm64 suffix

**Dockerfile Image**:
- Base: `arm64v8/ubuntu:24.04`
- Packages: Build tools, CMake, Python dev, dpkg utilities

**Fallback**: 
- Warns if ARM64 build fails
- Suggests native arm64 runner for production
- Does not fail release workflow if optional

#### 5. Create Release

**Output**: 
- GitHub Release with all assets
- SHA256SUMS file
- Release notes

**Assets Attached**:
1. Source package: `zedit-X.Y.Z-source.tar.gz`
2. Debian AMD64: `zedit-X.Y.Z-amd64.deb` (required)
3. Debian ARM64: `zedit-X.Y.Z-arm64.deb` (optional, if built)

**Steps**:
- Download all build artifacts
- Verify asset presence
- Generate SHA256 checksums for all files
- Create SHA256SUMS file
- Create GitHub Release with:
  - Auto-generated release notes
  - All artifacts attached
  - Draft: false (published immediately)
  - Prerelease: false (stable release)

**Release Notes**:
- Auto-generated from commits since last tag
- Manual review possible via draft mode

## Usage Examples

### Triggering a Release

```bash
# Tag a new release (locally)
git tag v0.6.6
git push origin v0.6.6

# The release workflow triggers automatically
# Check Actions tab on GitHub for progress
```

### Verifying Release Artifacts

```bash
# Download SHA256SUMS
wget https://github.com/pilakkat1964/z-edit/releases/download/v0.6.6/SHA256SUMS

# Verify all artifacts
sha256sum -c SHA256SUMS

# Output should show:
# zedit-0.6.6-source.tar.gz: OK
# zedit-0.6.6-amd64.deb: OK
# zedit-0.6.6-arm64.deb: OK (if available)
```

### Installing from Released Artifacts

#### From Debian Package (AMD64)

```bash
wget https://github.com/pilakkat1964/z-edit/releases/download/v0.6.6/zedit-0.6.6-amd64.deb
sudo dpkg -i zedit-0.6.6-amd64.deb
zedit --version
```

#### From Debian Package (ARM64)

```bash
wget https://github.com/pilakkat1964/z-edit/releases/download/v0.6.6/zedit-0.6.6-arm64.deb
sudo dpkg -i zedit-0.6.6-arm64.deb
zedit --version
```

#### From Source Archive

```bash
wget https://github.com/pilakkat1964/z-edit/releases/download/v0.6.6/zedit-0.6.6-source.tar.gz
tar -xzf zedit-0.6.6-source.tar.gz
cd zedit-0.6.6-source
pip install .
zedit --version
```

## Workflow Files

### CI Workflow Location
`.github/workflows/ci.yml` - 129 lines

### Release Workflow Location
`.github/workflows/release.yml` - 220+ lines

## Environment

### Build Environment
- **OS**: Ubuntu Latest (ubuntu-latest)
- **Python**: 3.11, 3.12 (tested in CI)
- **Tools**: 
  - cmake >= 3.10
  - Python 3.11+
  - uv >= 0.11.0
  - Docker (for multi-platform builds)
  - QEMU (for ARM64 emulation)

### Supported Platforms

**CI Tests**:
- Python 3.11
- Python 3.12

**Release Builds**:
- AMD64/x86_64 (primary)
- ARM64/aarch64 (Docker-based)

**Package Formats**:
- Debian (.deb) - AMD64
- Debian (.deb) - ARM64
- Source tarball (.tar.gz)

## Error Handling

### CI Workflow
- **Linting failures**: Non-blocking (continue-on-error)
- **Test failures**: Non-blocking (continue-on-error)
- **Security alerts**: Non-blocking (continue-on-error)
- **Build failures**: Blocking (stops workflow)

### Release Workflow
- **Source package failure**: Blocking (required)
- **AMD64 package failure**: Blocking (required)
- **ARM64 package failure**: Non-blocking (optional)
- **Checksum generation**: Blocking (required)

## Artifacts & Retention

### Build Artifacts
- **Retention**: 7 days (configurable)
- **Storage**: GitHub Actions artifact storage
- **Purpose**: Intermediate storage for build products

### Release Artifacts
- **Retention**: Permanent (on GitHub Releases)
- **Storage**: GitHub Releases assets
- **Purpose**: Public distribution

## Performance

### CI Workflow Execution Time
- Lint and Test: ~5-10 minutes
- Security Check: ~3-5 minutes
- Build Check: ~3-5 minutes
- **Total**: ~15-20 minutes

### Release Workflow Execution Time
- Prepare: ~1 minute
- Source Package: ~2 minutes
- AMD64 Build: ~10-15 minutes
- ARM64 Build: ~15-25 minutes (Docker + QEMU)
- Create Release: ~2 minutes
- **Total**: ~30-50 minutes

## Future Enhancements

Possible improvements:

1. **Native ARM64 Runner**: 
   - Faster builds than QEMU emulation
   - Requires GitHub Actions runner setup

2. **Multi-Distribution Packaging**:
   - RPM packages (Fedora/RHEL)
   - Arch packages (Arch Linux)
   - Alpine packages (Alpine Linux)

3. **Code Coverage**:
   - Codecov integration
   - Coverage reports in PRs

4. **Automated Changelog**:
   - Auto-generate CHANGELOG.md
   - Semantic versioning-based entries

5. **Security Scanning**:
   - SAST (Static Application Security Testing)
   - Dependency scanning
   - Container scanning

6. **Performance Benchmarks**:
   - Track build times
   - Performance regression detection

## Related Documentation

- [CI/CD Guide](./cicd-guide.md) - Detailed CI/CD setup
- [Build Guide](./build.md) - Build system details
- [Release Guide](../docs/cicd-guide.md) - Release procedures

## Troubleshooting

### Release Workflow Fails

**Check**:
1. Tag format matches `v*` pattern
2. Version is valid semantic versioning
3. GitHub token has write permissions
4. No existing artifacts with same name

### CI Workflow Fails

**Check**:
1. Code passes linting
2. Tests pass locally
3. Dependencies are installed
4. Python version is 3.11+

### ARM64 Build Fails

**Expected Behavior**:
- ARM64 failure is non-blocking
- Release still succeeds with AMD64 only
- Warning message displayed

**To Fix**:
- Use native ARM64 runner
- Or ignore ARM64 builds
- Or update QEMU/Docker configuration

---

**Last Updated**: April 15, 2026

For more information, see [GitHub Actions documentation](https://docs.github.com/en/actions)
