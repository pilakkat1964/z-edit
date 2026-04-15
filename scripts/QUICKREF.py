#!/usr/bin/env python3
"""
Quick reference for common dev.py workflows.

This file documents the most common use cases and their commands.
"""

# === INITIAL SETUP ===
# Run once to set up development environment:
#   ./scripts/dev.py setup

# === DAILY DEVELOPMENT ===
# After making changes:
#   ./scripts/dev.py build     # Rebuild
#   ./scripts/dev.py test      # Run tests
#
# Or in one command:
#   ./scripts/dev.py build && ./scripts/dev.py test

# === PREPARE RELEASE ===
# When ready to release version 0.2.0:
#   ./scripts/dev.py full --version 0.2.0
#
# This does: setup → build → test → package → release
# (setup is skipped if already done)

# === STEP-BY-STEP RELEASE ===
# More control with individual steps:
#   ./scripts/dev.py build
#   ./scripts/dev.py test
#   ./scripts/dev.py package
#   ./scripts/dev.py release --version 0.2.0

# === STAGING RELEASE ===
# Create a release candidate tag (v0.2.0-rc1-stage):
#   ./scripts/dev.py release --version 0.2.0-rc1 --stage

# === DRY RUN ===
# Test workflow without making changes:
#   ./scripts/dev.py full --version 0.2.0 --dry-run --verbose

# === FAST PACKAGING ===
# During development (skip DEB, just source):
#   ./scripts/dev.py package --skip-deb

# === ENVIRONMENT PROBLEMS ===
# Recreate virtual environment:
#   rm -rf .venv
#   ./scripts/dev.py setup

# === VERBOSE OUTPUT ===
# See all commands being executed:
#   ./scripts/dev.py build --verbose
#   ./scripts/dev.py full --version 0.2.0 --verbose


# QUICK REFERENCE TABLE
# =====================
# Command                                   | What it does
# ------------------------------------------|------------------------------------------
# ./scripts/dev.py setup                    | Create venv, install deps
# ./scripts/dev.py build                    | CMake build locally
# ./scripts/dev.py test                     | Run pytest with coverage
# ./scripts/dev.py package                  | Build DEB + source archive
# ./scripts/dev.py release --version 0.2.0  | Create release tag, trigger CI
# ./scripts/dev.py full --version 0.2.0     | Complete: setup→build→test→package→release
#
# Options you can add:
# ------------------------------------------|------------------------------------------
# -v, --verbose                             | Show all commands
# --dry-run                                 | Show what would happen
# --version VERSION                         | Specify version
# --stage                                   | Staging release (adds -stage to tag)
# --no-wait                                 | Don't wait for GitHub Actions
# --skip-deb                                | Skip DEB generation (faster)
# --skip-source                             | Skip source archive generation
