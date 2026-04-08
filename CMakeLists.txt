cmake_minimum_required(VERSION 3.20)

project(edit
    VERSION      0.1.0
    DESCRIPTION  "Smart file editor launcher"
    HOMEPAGE_URL "https://github.com/example/edit"
    LANGUAGES    NONE        # Python only — no C/C++ compiler needed
)

# ── Standard install directories (bin, lib, share, etc, doc …) ───────────────
# GNUInstallDirs needs at least one known arch to set LIBDIR; since this is a
# Python-only project (LANGUAGES NONE) we supply a sensible default ourselves.
if(NOT DEFINED CMAKE_INSTALL_LIBDIR)
    set(CMAKE_INSTALL_LIBDIR "lib" CACHE STRING "Object code libraries (lib)")
endif()
include(GNUInstallDirs)

# ── Python interpreter ────────────────────────────────────────────────────────
find_package(Python3 REQUIRED COMPONENTS Interpreter)

message(STATUS "Python: ${Python3_EXECUTABLE} (${Python3_VERSION})")

# ── Options ───────────────────────────────────────────────────────────────────
option(EDIT_BUILD_WHEEL
    "Build a Python wheel during the 'all' target (requires python-build)"
    ON)

option(EDIT_INSTALL_VIA_PIP
    "Install the Python package via pip instead of copying the script directly"
    OFF)

# The 'ed' alias saves a keystroke.  It is installed in user/local-admin
# locations (~/.local/bin, /opt/bin, /usr/local/bin) to avoid conflicts with
# the distro-managed classic ed(1) line editor at /usr/bin/ed.
# Run  `edit --install-alias`  to create the symlink interactively.
# Set EDIT_INSTALL_ED_ALIAS=OFF to suppress the automatic CMake install step.
option(EDIT_INSTALL_ED_ALIAS
    "Install an 'ed' symlink pointing at the 'edit' binary (into CMAKE_INSTALL_BINDIR)"
    ON)

# When installing under /usr (e.g. Debian packages), the system configuration
# directory is conventionally /etc, not /usr/etc.  GNUInstallDirs only makes
# this adjustment when CMAKE_INSTALL_PREFIX is exactly /usr at configure time,
# so we provide our own override that survives `cmake --install --prefix /usr`.
if(CMAKE_INSTALL_PREFIX STREQUAL "/usr")
    set(_default_sysconfdir "/etc")
else()
    set(_default_sysconfdir "${CMAKE_INSTALL_SYSCONFDIR}")
endif()
set(EDIT_SYSCONFDIR "${_default_sysconfdir}"
    CACHE PATH
    "Directory for system-wide configuration files (e.g. /etc or /usr/local/etc)")

# ── Wheel build target ────────────────────────────────────────────────────────
# Produces dist/edit-<version>-py3-none-any.whl
if(EDIT_BUILD_WHEEL)
    set(_WHEEL_STAMP "${CMAKE_BINARY_DIR}/dist/.stamp")

    add_custom_command(
        OUTPUT  "${_WHEEL_STAMP}"
        COMMAND "${Python3_EXECUTABLE}" -m build
                    --wheel
                    --no-isolation
                    --outdir "${CMAKE_BINARY_DIR}/dist"
        COMMAND "${CMAKE_COMMAND}" -E touch "${_WHEEL_STAMP}"
        DEPENDS
            "${CMAKE_SOURCE_DIR}/edit.py"
            "${CMAKE_SOURCE_DIR}/pyproject.toml"
        WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
        COMMENT "Building Python wheel for ${PROJECT_NAME} ${PROJECT_VERSION}"
        VERBATIM
    )

    add_custom_target(wheel ALL DEPENDS "${_WHEEL_STAMP}")
endif()

# ── Installation ──────────────────────────────────────────────────────────────
#
# Two mutually exclusive strategies:
#
#   EDIT_INSTALL_VIA_PIP=OFF  (default)
#     CMake copies the script and config directly.  This is the right choice
#     for distribution packages that handle Python paths themselves (e.g. dh).
#
#   EDIT_INSTALL_VIA_PIP=ON
#     CMake delegates to pip.  Useful for direct developer installs where you
#     want the full Python entry-points / .dist-info metadata.
#
if(EDIT_INSTALL_VIA_PIP)
    # pip-based install — drives pyproject.toml / setuptools
    install(CODE
        "execute_process(
            COMMAND \"${Python3_EXECUTABLE}\" -m pip install
                        --no-deps
                        --no-build-isolation
                        --prefix \"\${CMAKE_INSTALL_PREFIX}\"
                        \"${CMAKE_SOURCE_DIR}\"
            RESULT_VARIABLE _pip_rc
        )
        if(NOT _pip_rc EQUAL 0)
            message(FATAL_ERROR \"pip install failed (exit code \${_pip_rc})\")
        endif()"
        COMPONENT Runtime
    )
else()
    # Direct install — CMake owns the installed layout
    install(
        PROGRAMS    "${CMAKE_SOURCE_DIR}/edit.py"
        DESTINATION "${CMAKE_INSTALL_BINDIR}"
        RENAME      edit
        COMPONENT   Runtime
    )
endif()

# 'ed' symlink — points at the installed 'edit' binary.
# The symlink goes into CMAKE_INSTALL_FULL_BINDIR (e.g. /usr/local/bin for the
# default prefix /usr/local).  /usr/local/bin does not conflict with the
# distro-managed classic ed(1) at /usr/bin/ed.  For user-only installs, prefer
# `edit --install-alias` which targets ~/.local/bin with full conflict checking.
if(EDIT_INSTALL_ED_ALIAS)
    install(CODE
        "set(_bindir \"\$ENV{DESTDIR}${CMAKE_INSTALL_FULL_BINDIR}\")
        set(_link \"\${_bindir}/ed\")
        # Warn if an 'ed' already exists at this path and is not our symlink.
        if(EXISTS \"\${_link}\" OR IS_SYMLINK \"\${_link}\")
            execute_process(
                COMMAND \"${CMAKE_COMMAND}\" -E env readlink \"\${_link}\"
                OUTPUT_VARIABLE _target OUTPUT_STRIP_TRAILING_WHITESPACE
                ERROR_QUIET
            )
            if(NOT \"\${_target}\" STREQUAL \"edit\")
                message(WARNING \"'ed' already exists at \${_link} (→ \${_target}); skipping alias.\")
                return()
            else()
                message(STATUS \"'ed' alias already in place: \${_link} → edit\")
                return()
            endif()
        endif()
        execute_process(
            COMMAND \"${CMAKE_COMMAND}\" -E create_symlink edit \"\${_link}\"
            RESULT_VARIABLE _rc
        )
        if(NOT _rc EQUAL 0)
            message(WARNING \"Could not create ed symlink in \${_bindir}\")
        else()
            message(STATUS \"Symlinking: \${_link} → edit\")
        endif()"
        COMPONENT Runtime
    )
endif()
install(
    FILES       "${CMAKE_SOURCE_DIR}/config/default.toml"
    DESTINATION "${EDIT_SYSCONFDIR}/edit"
    RENAME      config.toml
    COMPONENT   Config
)

# Package documentation
install(
    FILES       "${CMAKE_SOURCE_DIR}/README.md"
    DESTINATION "${CMAKE_INSTALL_DOCDIR}"
    COMPONENT   Doc
)

install(
    DIRECTORY   "${CMAKE_SOURCE_DIR}/docs/"
    DESTINATION "${CMAKE_INSTALL_DOCDIR}/docs"
    COMPONENT   Doc
    FILES_MATCHING PATTERN "*.md"
)

# ── Packaging (CPack) ─────────────────────────────────────────────────────────
include(cmake/packaging.cmake)
