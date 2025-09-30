# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MusicLib** is a Python package that provides bindings for Apple's iTunes Library (ITlib) API, enabling programmatic access to iTunes/Music library data on macOS. It consists of:

- **Python package** (`src/musiclib/`) - Main Python interface with ctypes bindings
- **Swift bridge** (`src/SwiftITLibBridge.swift`) - Native Swift/iTunes Library interface compiled to `libitlibrary.dylib`
- **Architecture**: Python calls ctypes → Swift dylib → iTunes Library Framework

## Essential Development Commands

### Setup and Installation
```bash
# Install dependencies and setup development environment
make install-dev

# Check prerequisites (Swift, Python, NumPy, iTunes Library framework)
make check
```

### Build Process
```bash
# Build the Swift bridge library (required before running Python code)
make build

# The Swift compilation produces src/musiclib/libitlibrary.dylib
# This .dylib must exist before any Python code can run
```

### Development Workflow
```bash
# Complete development workflow
make all  # Equivalent to: check format lint typecheck install-dev test-cov

# Individual steps
make format      # Format with black
make lint        # Check with ruff
make lint-fix    # Auto-fix ruff issues
make typecheck   # Run mypy
make licensecheck # Check package licenses
```

### Testing
```bash
# Basic smoke test
make smoke

# Full test suite
make test

# Tests with coverage report (outputs to coverage/index.html)
make test-cov

# Run specific test
uv run pytest tests/test_itlibrary.py

# Skip slow performance tests during development
uv run pytest -m "not slow"

# Performance benchmarks
make benchmark
```

### Package Management
```bash
# Clean build artifacts
make clean

# Create distribution package
make dist

# Install from wheel to site-packages
make install

# Uninstall from site-packages
make uninstall

# Export library statistics
make export-stats

# Export sample library data to CSV
make export-sample
```

## Key Architecture Points

### Dependencies
- **macOS only** - Requires iTunes Library framework (macOS 10.7+)
- **Swift toolchain** - For compiling the bridge library
- **NumPy & Pandas** - Core dependencies for data handling and array operations
- **uv** - Package and dependency manager
- **Optional**: Pillow (for image processing), OpenPyXL (for Excel export)

### Core Components
- `musiclib.py` - Main Python API with iTunes Library classes (ITLibrary, MediaItem, Playlist, etc.)
- `helpers.py` - Higher-level utilities and performance benchmarks
- `SwiftITLibBridge.swift` - Swift/iTunes Library implementation that gets compiled to .dylib
- `scripts/` - Demo and smoke test entry points

### API Design
The Python API provides access to iTunes/Music library with classes like:
- `ITLibrary` - Main library interface and connection management
- `MediaItem` - Individual tracks/songs with metadata (title, artist, album, duration, etc.)
- `Playlist` - Playlist objects with name and item count
- Search functions for finding content by title or artist

### Testing Strategy
- `test_itlibrary.py` - Main functionality tests
- `test_library_lifecycle.py` - Resource management and lifecycle tests
- Performance tests marked with `@pytest.mark.slow`
- Tests automatically skip if no media content is available

## Important Notes

- **Swift compilation required**: The Python code cannot run without first building the Swift bridge with `make build`
- **macOS only**: Project includes explicit macOS detection and will fail on other platforms
- **iTunes Library access**: Requires iTunes/Music app and may require user permission on first access
- **Test organization**: Use `pytest -m "not slow"` to skip performance benchmarks during development
- **Package structure**: Uses modern Python packaging with `pyproject.toml` and `hatchling` build backend
- **Library content dependent**: Many tests will skip if no media items or playlists are found in the iTunes Library
- **Entry points**: Package provides CLI commands: `musiclib-demo`, `musiclib-smoke`, `musiclib-export`
- **Universal binaries**: Use `make build-universal` for ARM64 + x86_64 support