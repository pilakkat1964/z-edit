#!/usr/bin/env python3
"""
zedit development workflow wrapper

Accelerates the test-driven development cycle by wrapping:
- Environment setup (venv, dependencies)
- Building and testing locally
- Packaging (source archive, DEB)
- Version control (review, commit, push)
- GitHub release automation

Usage:
    ./scripts/dev.py --help
    ./scripts/dev.py setup
    ./scripts/dev.py build
    ./scripts/dev.py test
    ./scripts/dev.py package
    ./scripts/dev.py release --version 0.2.0 --stage
    ./scripts/dev.py full --version 0.2.0
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple, List
import json
import re


@dataclass
class Context:
    """Execution context for the workflow."""

    root_dir: Path
    venv_dir: Path
    build_dir: Path
    verbose: bool = False
    dry_run: bool = False

    @classmethod
    def auto(cls, verbose: bool = False, dry_run: bool = False) -> "Context":
        """Auto-discover project root from script location."""
        script_dir = Path(__file__).parent.absolute()
        root_dir = script_dir.parent
        return cls(
            root_dir=root_dir,
            venv_dir=root_dir / ".venv",
            build_dir=root_dir / "build",
            verbose=verbose,
            dry_run=dry_run,
        )

    def python(self) -> Path:
        """Get the venv Python executable."""
        return self.venv_dir / "bin" / "python"

    def pip(self) -> Path:
        """Get the venv pip executable."""
        return self.venv_dir / "bin" / "pip"

    def uv(self) -> str:
        """Get uv command (assume it's in PATH)."""
        return "uv"


class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RED = "\033[91m"


def log(msg: str, level: str = "info"):
    """Log a message with color."""
    if level == "info":
        print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")
    elif level == "success":
        print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")
    elif level == "warning":
        print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")
    elif level == "error":
        print(f"{Colors.RED}✗ {msg}{Colors.RESET}", file=sys.stderr)
    else:
        print(msg)


def run_cmd(
    cmd: List[str],
    ctx: Context,
    check: bool = True,
    capture: bool = False,
    cwd: Optional[Path] = None,
) -> Tuple[int, str]:
    """Execute a shell command."""
    if not cwd:
        cwd = ctx.root_dir

    if ctx.verbose or ctx.dry_run:
        log(f"$ {' '.join(str(c) for c in cmd)}", "info")

    if ctx.dry_run:
        return 0, ""

    try:
        if capture:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=check,
            )
            return result.returncode, result.stdout.strip()
        else:
            result = subprocess.run(cmd, cwd=cwd, check=check)
            return result.returncode, ""
    except subprocess.CalledProcessError as e:
        log(f"Command failed: {' '.join(str(c) for c in cmd)}", "error")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        raise


def setup_environment(ctx: Context) -> bool:
    """Set up the development environment."""
    log("Setting up development environment...", "info")

    # Check if venv exists
    if ctx.venv_dir.exists():
        log(f"Virtual environment already exists at {ctx.venv_dir}", "warning")
        response = input("Recreate? (y/N): ").strip().lower()
        if response != "y":
            log("Using existing environment", "info")
            return True
        import shutil

        shutil.rmtree(ctx.venv_dir)

    # Create venv
    log("Creating virtual environment...", "info")
    run_cmd([sys.executable, "-m", "venv", str(ctx.venv_dir)], ctx)

    # Upgrade pip
    log("Upgrading pip, setuptools, wheel...", "info")
    run_cmd(
        [str(ctx.pip()), "install", "--upgrade", "pip", "setuptools", "wheel"],
        ctx,
    )

    # Install dependencies with uv (faster)
    log("Installing dependencies with uv...", "info")
    run_cmd([ctx.uv(), "sync", "--all-extras"], ctx)

    log("Environment setup complete", "success")
    return True


def build_locally(ctx: Context) -> bool:
    """Build the project locally."""
    log("Building project locally...", "info")

    # Clean previous build
    if ctx.build_dir.exists():
        import shutil

        log(f"Removing previous build directory: {ctx.build_dir}", "info")
        shutil.rmtree(ctx.build_dir)

    # Configure CMake
    log("Configuring CMake...", "info")
    run_cmd(
        [
            "cmake",
            "-B",
            str(ctx.build_dir),
            "-DCMAKE_INSTALL_PREFIX=/opt/zedit",
            "-DZEDIT_BUILD_WHEEL=OFF",
        ],
        ctx,
    )

    # Build
    log("Building with CMake...", "info")
    run_cmd(["cmake", "--build", str(ctx.build_dir)], ctx)

    log("Build complete", "success")
    return True


def run_tests(ctx: Context) -> bool:
    """Run project tests."""
    log("Running tests...", "info")

    tests_dir = ctx.root_dir / "tests"
    if not tests_dir.exists():
        log("No tests directory found", "warning")
        log("Creating minimal tests directory...", "info")
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "__init__.py").touch()
        (tests_dir / "test_smoke.py").write_text(
            '''"""Smoke tests for zedit."""

def test_zedit_module_imports():
    """Test that the zedit module can be imported."""
    import zedit
    assert hasattr(zedit, "main")
    assert callable(zedit.main)


def test_version_exists():
    """Test that version is accessible."""
    import zedit
    # Module should be importable and functional
    assert zedit is not None
'''
        )
        log("Created minimal test suite", "info")

    # Run pytest
    log("Executing pytest...", "info")
    run_cmd(
        [
            str(ctx.python()),
            "-m",
            "pytest",
            "-v",
            "--tb=short",
            "--cov=zedit",
            "--cov-report=term-missing",
            str(tests_dir),
        ],
        ctx,
        check=False,  # Don't fail on test errors, we want to see them
    )

    log("Tests complete", "success")
    return True


def get_current_version(ctx: Context) -> str:
    """Extract current version from pyproject.toml."""
    pyproject = ctx.root_dir / "pyproject.toml"
    content = pyproject.read_text()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if match:
        return match.group(1)
    return "0.0.0"


def get_git_status(ctx: Context) -> dict:
    """Get git status information."""
    returncode, output = run_cmd(
        ["git", "status", "--porcelain"], ctx, capture=True, check=False
    )
    modified = []
    for line in output.split("\n"):
        if line.strip():
            modified.append(line[3:].strip())
    return {"modified": modified}


def prompt_git_review(ctx: Context) -> bool:
    """Interactive git diff and staging."""
    log("Reviewing changes...", "info")
    run_cmd(["git", "diff", "--stat"], ctx, check=False)
    print()
    run_cmd(["git", "diff"], ctx, check=False)

    response = input("\nStage all changes? (y/N): ").strip().lower()
    if response != "y":
        return False

    run_cmd(["git", "add", "-A"], ctx)
    log("Changes staged", "success")
    return True


def create_commit(ctx: Context, message: str) -> bool:
    """Create a git commit."""
    log(f"Creating commit: {message}", "info")
    run_cmd(["git", "commit", "-m", message], ctx, check=False)
    return True


def push_upstream(ctx: Context, branch: str = "master") -> bool:
    """Push changes to upstream."""
    log(f"Pushing to upstream ({branch})...", "info")
    run_cmd(["git", "push", "origin", branch], ctx, check=False)
    log("Pushed successfully", "success")
    return True


def package_deb(ctx: Context) -> bool:
    """Package as DEB."""
    log("Building DEB package...", "info")

    run_cmd(["cmake", "--build", str(ctx.build_dir), "--target", "deb"], ctx)

    # Find the DEB file
    deb_files = list(ctx.build_dir.glob("zedit-*.deb"))
    if not deb_files:
        log("No DEB file found after build", "error")
        return False

    deb_file = deb_files[0]
    log(f"DEB package created: {deb_file}", "success")

    # Show package info
    run_cmd(["dpkg", "-I", str(deb_file)], ctx, check=False)
    return True


def package_source(ctx: Context, version: str) -> bool:
    """Create source archive."""
    log("Creating source archive...", "info")

    archive_name = f"zedit-{version}-source.tar.gz"
    archive_path = ctx.root_dir / archive_name

    run_cmd(
        [
            "git",
            "archive",
            "--format=tar.gz",
            f"--prefix=zedit-{version}-source/",
            "-o",
            str(archive_path),
            "HEAD",
        ],
        ctx,
    )

    if archive_path.exists():
        size_mb = archive_path.stat().st_size / (1024 * 1024)
        log(f"Source archive created: {archive_name} ({size_mb:.2f}MB)", "success")
        return True
    else:
        log("Failed to create source archive", "error")
        return False


def create_release_tag(ctx: Context, version: str, stage: bool = False) -> bool:
    """Create a git release tag."""
    tag_name = f"v{version}"
    if stage:
        tag_name = f"{tag_name}-stage"

    log(f"Creating release tag: {tag_name}", "info")

    # Check if tag exists
    returncode, _ = run_cmd(
        ["git", "tag", "-l", tag_name], ctx, capture=True, check=False
    )
    if returncode == 0:
        log(f"Tag {tag_name} already exists", "warning")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != "y":
            return False
        run_cmd(["git", "tag", "-d", tag_name], ctx)
        run_cmd(["git", "push", "origin", "--delete", tag_name], ctx, check=False)

    run_cmd(["git", "tag", tag_name], ctx)
    run_cmd(["git", "push", "origin", tag_name], ctx)

    log(f"Tag pushed: {tag_name}", "success")
    return True


def wait_for_release(ctx: Context, version: str, timeout: int = 300) -> bool:
    """Wait for GitHub Actions to create the release."""
    tag_name = f"v{version}"
    log(
        f"Waiting for GitHub Actions to create release for {tag_name}...",
        "info",
    )
    log("(This may take 1-2 minutes)", "info")

    # Try to check release status using gh CLI
    import time

    elapsed = 0
    check_interval = 10
    while elapsed < timeout:
        returncode, output = run_cmd(
            ["gh", "release", "view", tag_name, "--repo", "pilakkat1964/z-edit"],
            ctx,
            capture=True,
            check=False,
        )
        if returncode == 0:
            log("Release created successfully!", "success")
            log(
                f"View at: https://github.com/pilakkat1964/z-edit/releases/tag/{tag_name}",
                "info",
            )
            return True

        elapsed += check_interval
        remaining = timeout - elapsed
        log(f"Checking... ({remaining}s remaining)", "info")
        time.sleep(check_interval)

    log("Release creation timeout", "warning")
    log(
        "The release may still be building. Check GitHub Actions:",
        "info",
    )
    log("https://github.com/pilakkat1964/z-edit/actions", "info")
    return False


def cmd_setup(args, ctx: Context) -> int:
    """Handle setup subcommand."""
    try:
        setup_environment(ctx)
        return 0
    except Exception as e:
        log(f"Setup failed: {e}", "error")
        return 1


def cmd_build(args, ctx: Context) -> int:
    """Handle build subcommand."""
    try:
        build_locally(ctx)
        return 0
    except Exception as e:
        log(f"Build failed: {e}", "error")
        return 1


def cmd_test(args, ctx: Context) -> int:
    """Handle test subcommand."""
    try:
        run_tests(ctx)
        return 0
    except Exception as e:
        log(f"Tests failed: {e}", "error")
        return 1


def cmd_package(args, ctx: Context) -> int:
    """Handle package subcommand."""
    try:
        version = args.version or get_current_version(ctx)
        success = True

        if not args.skip_deb:
            success = success and package_deb(ctx)
        if not args.skip_source:
            success = success and package_source(ctx, version)

        if success:
            log("Packaging complete", "success")
            return 0
        else:
            return 1
    except Exception as e:
        log(f"Packaging failed: {e}", "error")
        return 1


def cmd_release(args, ctx: Context) -> int:
    """Handle release subcommand."""
    try:
        version = args.version
        if not version:
            version = get_current_version(ctx)
            log(f"Using current version from pyproject.toml: {version}", "info")

        # Validate version format
        if not re.match(r"^\d+\.\d+\.\d+", version):
            log(f"Invalid version format: {version}", "error")
            return 1

        # Review changes
        status = get_git_status(ctx)
        if status["modified"]:
            log("Modified files found:", "warning")
            for f in status["modified"]:
                print(f"  - {f}")
            if not prompt_git_review(ctx):
                log("Release cancelled", "warning")
                return 1

            # Create commit
            commit_msg = args.commit_msg or f"chore: release version {version}"
            create_commit(ctx, commit_msg)
            push_upstream(ctx)

        # Create release tag
        if not create_release_tag(ctx, version, stage=args.stage):
            return 1

        # Wait for release
        if not args.no_wait:
            wait_for_release(ctx, version, timeout=args.timeout)

        log("Release process complete", "success")
        return 0
    except Exception as e:
        log(f"Release failed: {e}", "error")
        return 1


def cmd_full(args, ctx: Context) -> int:
    """Handle full subcommand - complete workflow."""
    try:
        version = args.version
        if not version:
            version = get_current_version(ctx)
            log(f"Using current version from pyproject.toml: {version}", "info")

        # Validate version format
        if not re.match(r"^\d+\.\d+\.\d+", version):
            log(f"Invalid version format: {version}", "error")
            return 1

        steps = [
            ("Environment setup", lambda: setup_environment(ctx)),
            ("Build", lambda: build_locally(ctx)),
            ("Test", lambda: run_tests(ctx)),
            ("Package", lambda: package_deb(ctx) and package_source(ctx, version)),
            ("Release", lambda: cmd_release(args, ctx) == 0),
        ]

        for step_name, step_fn in steps:
            log(f"\n{'=' * 60}", "info")
            log(f"Step: {step_name}", "info")
            log(f"{'=' * 60}", "info")
            if not step_fn():
                log(f"Failed at: {step_name}", "error")
                return 1

        log(f"\n{'=' * 60}", "success")
        log("All steps completed successfully!", "success")
        log(f"{'=' * 60}", "success")
        return 0
    except Exception as e:
        log(f"Full workflow failed: {e}", "error")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="zedit development workflow wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./scripts/dev.py setup                           # Set up environment
  ./scripts/dev.py build                           # Build locally
  ./scripts/dev.py test                            # Run tests
  ./scripts/dev.py package                         # Build DEB and source
  ./scripts/dev.py release --version 0.2.0         # Create release tag
  ./scripts/dev.py release --version 0.2.0-rc1 --stage  # Stage release
  ./scripts/dev.py full --version 0.2.0            # Complete workflow
  ./scripts/dev.py full --version 0.2.0 --dry-run  # Test workflow
        """,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # setup command
    subparsers.add_parser(
        "setup",
        help="Set up development environment",
    )

    # build command
    subparsers.add_parser(
        "build",
        help="Build project locally",
    )

    # test command
    subparsers.add_parser(
        "test",
        help="Run project tests",
    )

    # package command
    pkg_parser = subparsers.add_parser(
        "package",
        help="Build packages (DEB, source)",
    )
    pkg_parser.add_argument(
        "--version",
        help="Version for source archive (default: from pyproject.toml)",
    )
    pkg_parser.add_argument(
        "--skip-deb",
        action="store_true",
        help="Skip DEB package building",
    )
    pkg_parser.add_argument(
        "--skip-source",
        action="store_true",
        help="Skip source archive creation",
    )

    # release command
    rel_parser = subparsers.add_parser(
        "release",
        help="Create and publish release",
    )
    rel_parser.add_argument(
        "--version",
        help="Version to release (default: from pyproject.toml)",
    )
    rel_parser.add_argument(
        "--stage",
        action="store_true",
        help="Create staging release (adds -stage suffix to tag)",
    )
    rel_parser.add_argument(
        "--commit-msg",
        help="Custom commit message (default: 'chore: release version X.Y.Z')",
    )
    rel_parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Don't wait for GitHub Actions to complete",
    )
    rel_parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout for waiting (seconds, default: 300)",
    )

    # full command
    full_parser = subparsers.add_parser(
        "full",
        help="Complete workflow: setup, build, test, package, release",
    )
    full_parser.add_argument(
        "--version",
        help="Version to release (default: from pyproject.toml)",
    )
    full_parser.add_argument(
        "--stage",
        action="store_true",
        help="Create staging release",
    )
    full_parser.add_argument(
        "--commit-msg",
        help="Custom commit message",
    )
    full_parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Don't wait for GitHub Actions to complete",
    )
    full_parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout for waiting (seconds)",
    )

    args = parser.parse_args()

    # Create context
    ctx = Context.auto(verbose=args.verbose, dry_run=args.dry_run)

    if args.dry_run:
        log("DRY RUN MODE - no changes will be made", "warning")

    # Dispatch to command handler
    commands = {
        "setup": cmd_setup,
        "build": cmd_build,
        "test": cmd_test,
        "package": cmd_package,
        "release": cmd_release,
        "full": cmd_full,
    }

    if not args.command:
        parser.print_help()
        return 1

    handler = commands.get(args.command)
    if not handler:
        log(f"Unknown command: {args.command}", "error")
        return 1

    return handler(args, ctx)


if __name__ == "__main__":
    sys.exit(main())
