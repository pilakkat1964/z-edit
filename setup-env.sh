#!/usr/bin/env bash
#
# z-edit Build Environment Setup Script
#
# This script checks and reports on project dependencies, with optional installation.
# It verifies Python version, uv tool, system-level dependencies, and optional packages.
#
# Usage:
#   ./setup-env.sh              # Check dependencies only (dry-run)
#   ./setup-env.sh --install    # Check and interactively install
#   ./setup-env.sh --force      # Check and install everything without prompting
#   ./setup-env.sh --help       # Show help message
#

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="z-edit (zedit)"
MIN_PYTHON_VERSION="3.11"
VENV_DIR="${SCRIPT_DIR}/.venv"

# State tracking
DRY_RUN=true
FORCE_INSTALL=false
INSTALL_MODE=false
DEPS_OK=true
WARNINGS=()
ERRORS=()

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo -e "\n${BLUE}=== ${PROJECT_NAME}: Build Environment Setup ===${NC}\n"
}

print_section() {
    echo -e "\n${BLUE}▶ $1${NC}"
}

print_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS+=("$1")
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    ERRORS+=("$1")
    DEPS_OK=false
}

print_info() {
    echo -e "  $1"
}

show_help() {
    cat << 'EOF'
z-edit Build Environment Setup Script

USAGE:
  ./setup-env.sh [OPTIONS]

OPTIONS:
  --help              Show this help message and exit
  --dry-run           Check dependencies without installing (default)
  --install           Check and interactively prompt for installation
  --force             Check and install everything without prompting

WHAT IT CHECKS:
  • Python version (>= 3.11)
  • uv tool availability
  • System-level dependencies (libmagic for python-magic)
  • Project dependencies via uv
  • Optional extras (magic, dev)

EXAMPLES:
  # Check dependencies only
  ./setup-env.sh

  # Check and prompt for installation
  ./setup-env.sh --install

  # Install everything without prompting
  ./setup-env.sh --force

EOF
}

confirm_action() {
    local prompt="$1"
    local response
    
    if [[ $FORCE_INSTALL == true ]]; then
        return 0
    fi
    
    echo -ne "${YELLOW}${prompt}${NC} (y/n): "
    read -r response
    
    case "$response" in
        [yY][eE][sS]|[yY])
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# ============================================================================
# Dependency Checks
# ============================================================================

check_python_version() {
    print_section "Checking Python Installation"
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 not found in PATH"
        return 1
    fi
    
    local py_version
    py_version=$(python3 --version 2>&1 | awk '{print $2}')
    
    print_ok "Python3 found: version $py_version"
    
    # Compare versions (semantic versioning comparison)
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
        print_ok "Python version meets minimum requirement (>= $MIN_PYTHON_VERSION)"
        return 0
    else
        print_error "Python version must be >= $MIN_PYTHON_VERSION (found: $py_version)"
        return 1
    fi
}

check_uv_tool() {
    print_section "Checking uv Tool Installation"
    
    if ! command -v uv &> /dev/null; then
        print_error "uv tool not found in PATH"
        print_info "Install uv from: https://docs.astral.sh/uv/getting-started/"
        return 1
    fi
    
    local uv_version
    uv_version=$(uv --version 2>&1)
    
    print_ok "uv tool found: $uv_version"
    return 0
}

check_libmagic() {
    print_section "Checking System Dependencies"
    
    if command -v ldconfig &> /dev/null; then
        if ldconfig -p | grep -q libmagic.so; then
            print_ok "libmagic development library found (for python-magic)"
            return 0
        fi
    fi
    
    # Fallback check
    if ldconfig -p 2>/dev/null | grep -q libmagic || pkg-config --exists libmagic 2>/dev/null; then
        print_ok "libmagic development library found (for python-magic)"
        return 0
    fi
    
    print_warn "libmagic not detected (optional, needed for accurate MIME detection)"
    print_info "On Ubuntu/Debian: sudo apt-get install libmagic1"
    print_info "On macOS: brew install libmagic"
    print_info "On Fedora: sudo dnf install file-devel"
    return 1
}

check_uv_venv() {
    print_section "Checking Virtual Environment"
    
    if [[ -d "$VENV_DIR" ]]; then
        print_ok "Virtual environment exists at: $VENV_DIR"
        return 0
    else
        print_warn "Virtual environment not yet created"
        return 1
    fi
}

check_project_dependencies() {
    print_section "Checking Project Dependencies"
    
    if [[ ! -f "${SCRIPT_DIR}/pyproject.toml" ]]; then
        print_error "pyproject.toml not found in: $SCRIPT_DIR"
        return 1
    fi
    
    print_ok "pyproject.toml found"
    
    if [[ ! -f "${SCRIPT_DIR}/uv.lock" ]]; then
        print_warn "uv.lock not found (will be generated)"
        return 1
    fi
    
    print_ok "uv.lock found"
    return 0
}

# ============================================================================
# Installation Functions
# ============================================================================

install_venv() {
    print_section "Creating Virtual Environment"
    
    if confirm_action "Create virtual environment with uv sync?"; then
        print_info "Running: uv sync --all-extras"
        cd "$SCRIPT_DIR"
        if uv sync --all-extras; then
            print_ok "Virtual environment created successfully"
            return 0
        else
            print_error "Failed to create virtual environment"
            return 1
        fi
    else
        print_warn "Skipped virtual environment creation"
        return 1
    fi
}

install_libmagic() {
    print_section "Installing System Dependencies"
    
    if confirm_action "Attempt to install libmagic (may require sudo)?"; then
        if command -v apt-get &> /dev/null; then
            print_info "Using apt-get to install libmagic1"
            sudo apt-get update
            sudo apt-get install -y libmagic1
        elif command -v brew &> /dev/null; then
            print_info "Using brew to install libmagic"
            brew install libmagic
        elif command -v dnf &> /dev/null; then
            print_info "Using dnf to install file-devel"
            sudo dnf install -y file-devel
        else
            print_warn "Could not detect package manager"
            return 1
        fi
    else
        print_warn "Skipped libmagic installation"
        return 1
    fi
}

# ============================================================================
# Report Functions
# ============================================================================

print_summary() {
    echo ""
    echo -e "${BLUE}=== Summary ===${NC}"
    
    if [[ ${#ERRORS[@]} -gt 0 ]]; then
        echo -e "\n${RED}Errors (${#ERRORS[@]}):${NC}"
        for err in "${ERRORS[@]}"; do
            echo -e "  ${RED}✗${NC} $err"
        done
    fi
    
    if [[ ${#WARNINGS[@]} -gt 0 ]]; then
        echo -e "\n${YELLOW}Warnings (${#WARNINGS[@]}):${NC}"
        for warn in "${WARNINGS[@]}"; do
            echo -e "  ${YELLOW}⚠${NC} $warn"
        done
    fi
    
    if [[ $DEPS_OK == true && ${#ERRORS[@]} -eq 0 ]]; then
        echo -e "\n${GREEN}✓ All critical dependencies are satisfied!${NC}"
    else
        echo -e "\n${RED}✗ Some critical dependencies are missing.${NC}"
    fi
}

print_next_steps() {
    echo -e "\n${BLUE}=== Next Steps ===${NC}"
    
    if [[ -d "$VENV_DIR" ]]; then
        echo -e "\n${GREEN}Virtual environment is ready!${NC}"
        echo ""
        echo "Activate the environment:"
        echo "  source .venv/bin/activate"
        echo ""
        echo "Try the tool:"
        echo "  zedit --help"
        echo "  zedit --list"
        echo ""
    else
        echo -e "\n${YELLOW}Virtual environment not created.${NC}"
        echo ""
        echo "To set up the environment, run:"
        echo "  ./setup-env.sh --install"
        echo ""
    fi
    
    if [[ ${#WARNINGS[@]} -gt 0 ]]; then
        echo -e "\n${YELLOW}Optional improvements:${NC}"
        echo "  • Review warnings above for optional dependencies"
        echo "  • Consider installing libmagic for better MIME detection"
        echo ""
    fi
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    local install_libmagic_opt=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --help)
                show_help
                exit 0
                ;;
            --install)
                DRY_RUN=false
                INSTALL_MODE=true
                shift
                ;;
            --force)
                DRY_RUN=false
                INSTALL_MODE=true
                FORCE_INSTALL=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                INSTALL_MODE=false
                shift
                ;;
            *)
                echo "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_header
    
    # Run all checks
    check_python_version || true
    check_uv_tool || true
    check_libmagic || true
    check_uv_venv || true
    check_project_dependencies || true
    
    # If not in dry-run mode, offer to install
    if [[ $INSTALL_MODE == true ]]; then
        echo ""
        print_section "Installation Phase"
        
        # Check if libmagic needs installation
        if ! ldconfig -p 2>/dev/null | grep -q libmagic.so; then
            install_libmagic_opt=true
        fi
        
        # Create/update virtual environment
        install_venv || true
    fi
    
    print_summary
    print_next_steps
    
    if [[ $DEPS_OK == true ]]; then
        exit 0
    else
        exit 1
    fi
}

# Run main function
main "$@"
